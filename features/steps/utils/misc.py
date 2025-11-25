import warnings
import ifcopenshell
import operator
import pyparsing

from typing import Iterable, Iterator, Sequence, Union, Optional
import numpy as np
from numbers import Real

def reverse_operands(fn):
    """
    Given a function `fn` that operates on two arguments, the returned function will
    swap the order of these arguments before applying `fn`.

    For instance, with the function operator.contains which expects argument in a specific order. 
        contains_reversed = reverse_operands(operator.contains)
        contains_reversed(3, [1, 2, 3, 4])  # True
        operator.contains([1,2,3,4], 3) # True

        However
        operator.contains(3, [1,2,3,4]) # Raises a TypeError
    """
    def inner(*args):
        return fn(*reversed(args))
    return inner


def recursive_flatten(lst):
    flattened_list = []
    for item in lst:
        if isinstance(item, (tuple, list, PackedSequence)):
            flattened_list.extend(recursive_flatten(item))
        else:
            flattened_list.append(item)
    return flattened_list


def iflatten(any):
    if isinstance(any, (tuple, list, PackedSequence)):
        for v in any:
            yield from iflatten(v)
    else:
        yield any


def do_try(fn, default=None):
    try:
        return fn()
    except:
        return default

# @note dataclasses.asdict used deepcopy() which doesn't work on entity instance
asdict = lambda dc: dict(instance_converter(dc.__dict__.items()), message=str(dc), **dict(get_inst_attributes(dc)))


def get_inst_attributes(dc):
    if hasattr(dc, 'inst'):
        if isinstance(dc.inst, ifcopenshell.entity_instance):
            yield 'inst_guid', getattr(dc.inst, 'GlobalId', None)
            yield 'inst_type', dc.inst.is_a()
            yield 'inst_id', dc.inst.id()
        else:
            # apparently mostly for the rule passed logs...
            # @todo fix this
            yield 'inst_guid', None
            yield 'inst_type', type(dc.inst).__name__


def fmt(x):
    if isinstance(x, frozenset) and len(x) == 2 and set(map(type, x)) == {tuple}:
        return "{} -- {}".format(*x)
    elif isinstance(x, tuple) and len(x) == 2 and set(map(type, x)) == {tuple}:
        return "{} -> {}".format(*x)
    else:
        v = str(x)
        if len(v) > 35:
            return "...".join((v[:25], v[-7:]))
        return v

def include_subtypes(stmt):
    # todo replace by pyparsing?
    stmt = strip_split(stmt, strp='[]', splt=' ')
    excluding_statements = {'without', 'not', 'excluding', 'no'}
    return not set(stmt).intersection(set(excluding_statements))


def instance_converter(kv_pairs):
    def c(v):
        if isinstance(v, ifcopenshell.entity_instance):
            return str(v)
        else:
            return v
    return {k: c(v) for k, v in kv_pairs}


def is_a(s):
    return lambda inst: inst.is_a(s)

def make_aggregrated_dict(table, ent_tbl_header, relationship_tbl_header):
    aggregated_table = {}
    for d in table:
        applicable_entity = d[ent_tbl_header]
        tbl_relationship_object = d[relationship_tbl_header]
        if applicable_entity in aggregated_table:
            aggregated_table[applicable_entity].append(tbl_relationship_object)
        else:
            aggregated_table[applicable_entity] = [tbl_relationship_object]
    return aggregated_table


def map_state(values, fn):
    if isinstance(values, (tuple, list)):
        return type(values)(map_state(v, fn) for v in values)
    else:
        return fn(values)


def rtrn_pyparse_obj(i):
    if isinstance(i, (pyparsing.core.LineEnd, pyparsing.core.NotAny)):
        return i
    elif isinstance(i, str):
        return pyparsing.CaselessKeyword(i)


def stmt_to_op(statement):
    statement = statement.replace('is', '').strip()
    statement = statement.lower()
    stmts_to_op = {
        '': operator.eq,  # a == b
        "equal to": operator.eq,  # a == b
        "exactly": operator.eq,  # a == b
        "not": operator.ne,  # a != b
        "at least": operator.ge,  # a >= b
        "more than": operator.gt,  # a > b
        "at most": operator.le,  # a <= b
        "less than": operator.lt  # a < b
    }
    assert statement in stmts_to_op
    return stmts_to_op[statement]


def strip_split(stmt, strp=" '", splt=",", lower=True, convert_num=True):
    """
    Splits a string by a delimiter, strips unwanted characters from each part,
    optionally converts to lowercase, and converts numeric strings to integers.

    Returns a tuple, to use with startswith()
    """
    def clean(s):
        s = s.strip(strp)
        return int(s) if convert_num and s.isdigit() else s

    return tuple(clean(s) for s in (stmt.lower() if lower else stmt).split(splt))




def unpack_sequence_of_entities(instances):
    # in case of [[inst1, inst2], [inst3, inst4]]
    return [do_try(lambda: unpack_tuple(inst), None) for inst in instances]


def unpack_tuple(tup):
    for item in tup:
        if isinstance(item, tuple):
            unpack_tuple(item)
        else:
            return item

def define_feature_version(context):
    version = next((tag for tag in context.tags if "version" in tag))  # e.g. version1
    return int(version.replace("version", ""))


def recursive_unpack_value(item):
    """Unpacks a tuple recursively, returning the first non-empty item
    For instance, (,'Body') will return 'Axis'
    and (((IfcEntityInstance.)),) will return IfcEntityInstance

    Note that it will only work for a single value. E.g. not values for statements like 
    "The values must be X"
    as ('Axis', 'Body') will return 'Axis' 
    """
    if isinstance(item, (tuple, list)):
        if len(item) == 0:
            return None
        elif len(item) == 1 or not item[0]:
            return recursive_unpack_value(item[1]) if len(item) > 1 else recursive_unpack_value(item[0])
        else:
            return item[0]
    return item

def get_stack_tree(context):
    """Returns the stack tree of the current context. To be used for 'attribute stacking', e.g. in GEM004"""
    return list(
        filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))

TNum = Union[int, float, np.number]

class ContiguousSet:
    """
    A set-like container for numeric values backed by:
      - a sorted, contiguous NumPy array (committed data) for memory compactness
      - a Python set for pending inserts (amortized commits)

    Features
    --------
    - Only accepts numeric (int/float/np.number); rejects bool and non-finite values (NaN/Inf).
    - Membership: O(log n) via binary search on the array.
    - Iteration yields sorted ascending order without forcing commit.
    - No remove/discard support
    - `commit()` merges pending into the array; auto-commit when `pending_max` is reached.
    """

    __slots__ = ("_arr", "_pending", "_dtype", "_pending_max")

    def __init__(
        self,
        data: Optional[Iterable[TNum]] = None,
        *,
        dtype: np.dtype = np.int64,
        pending_max: int = 1024,
    ) -> None:
        """
        Parameters
        ----------
        data : optional iterable of numeric
            Initial values (deduplicated).
        dtype : NumPy dtype, default float64
            Storage dtype for the NumPy array.
        pending_max : int, default 1024
            Auto-commit threshold for number of pending items.
        """
        self._dtype = np.dtype(dtype)
        self._pending_max = int(pending_max)
        self._arr = np.ascontiguousarray(np.array([], dtype=self._dtype))
        self._pending: set = set()
        if data is not None:
            self.update(data)
            self.commit()

    @staticmethod
    def _is_number(x) -> bool:
        return isinstance(x, Real) and not isinstance(x, bool)

    def _check_numeric(self, x):
        if not self._is_number(x):
            raise TypeError(f"Only numeric (int/float) values allowed, got {type(x).__name__}")
        # Reject NaN/Inf — they break equality/ordering semantics
        if not np.isfinite(x):
            raise ValueError("Values must be finite (no NaN/Inf).")

    def _in_array(self, x: TNum) -> bool:
        if self._arr.size == 0:
            return False
        idx = np.searchsorted(self._arr, x, side="left")
        return (idx < self._arr.size) and (self._arr[idx] == x)

    def _maybe_autocommit(self) -> None:
        if len(self._pending) >= self._pending_max:
            self.commit()

    def add(self, x: TNum) -> None:
        """Add a numeric value. No effect if it's already present."""
        self._check_numeric(x)
        if x in self._pending:
            return
        if self._in_array(x):
            return
        self._pending.add(x)
        self._maybe_autocommit()

    def update(self, values: Iterable[TNum]) -> None:
        """Add many values efficiently (does not force commit)."""
        new_items = []
        for v in values:
            self._check_numeric(v)
            if (v in self._pending) or self._in_array(v):
                continue
            new_items.append(v)
        if new_items:
            self._pending.update(new_items)
            self._maybe_autocommit()

    def commit(self) -> None:
        """Merge pending items into the contiguous sorted NumPy array."""
        if not self._pending:
            return
        pend_arr = np.fromiter(self._pending, dtype=self._dtype, count=len(self._pending))
        if self._arr.size == 0:
            merged = np.unique(pend_arr)
        else:
            merged = np.union1d(self._arr, pend_arr)  # sorted, unique
        self._arr = np.ascontiguousarray(merged.astype(self._dtype, copy=False))
        self._pending.clear()

    def __contains__(self, x: object) -> bool:
        if not self._is_number(x):
            return False
        return (x in self._pending) or self._in_array(x)

    def __len__(self) -> int:
        # pending items are maintained disjoint from the array
        return int(self._arr.size + len(self._pending))

    def __iter__(self) -> Iterator[TNum]:
        """Iterate in ascending order without forcing a commit."""
        if not self._pending:
            # Fast path: just yield the array
            yield from self._arr.tolist()
            return

        pend_sorted = sorted(self._pending)
        i = j = 0
        n, m = self._arr.size, len(pend_sorted)
        while i < n and j < m:
            ai = self._arr[i]
            bj = pend_sorted[j]
            if ai < bj:
                yield ai; i += 1
            elif bj < ai:
                yield bj; j += 1
            else:
                yield ai; i += 1; j += 1
        while i < n:
            yield self._arr[i]; i += 1
        while j < m:
            yield pend_sorted[j]; j += 1

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        preview = list(self.__iter__())
        return f"{cls}({preview!r}, dtype={self._dtype!r}, pending={len(self._pending)})"

    def clear(self) -> None:
        """Remove all items (both committed and pending)."""
        self._arr = np.ascontiguousarray(np.array([], dtype=self._dtype))
        self._pending.clear()

    def copy(self) -> "ContiguousSet":
        """Shallow copy with copies of array & pending set."""
        new = ContiguousSet(dtype=self._dtype, pending_max=self._pending_max)
        new._arr = self._arr.copy()
        new._pending = set(self._pending)
        return new

    def isdisjoint(self, other: Iterable[TNum]) -> bool:
        s_other = {x for x in other if self._is_number(x)}
        if self._pending.intersection(s_other):
            return False
        for x in s_other:
            if self._in_array(x):
                return False
        return True

    def issubset(self, other: Iterable[TNum]) -> bool:
        s_other = {x for x in other if self._is_number(x)}
        if not self._pending.issubset(s_other):
            return False
        for x in self._arr:
            if x not in s_other:
                return False
        return True

    def union(self, other: Iterable[TNum]) -> "ContiguousSet":
        out = self.copy()
        out.update(other)
        return out

    def to_numpy(self, *, commit: bool = False) -> np.ndarray:
        if commit:
            self.commit()
            return self._arr
        if not self._pending:
            return self._arr.copy()
        merged = np.fromiter(self.__iter__(), dtype=self._dtype, count=len(self))
        return np.ascontiguousarray(merged)

    @property
    def dtype(self) -> np.dtype:
        return self._dtype

    @property
    def pending_size(self) -> int:
        return len(self._pending)

    @property
    def pending_max(self) -> int:
        return self._pending_max

    @pending_max.setter
    def pending_max(self, value: int) -> None:
        self._pending_max = int(value)

from array import array

TAG_TUPLE = 0
TAG_ARRAY = 1
TAG_SINGULAR_INT = 2
TAG_NONE = 3

class PackedBuilder:
    """
    Streaming builder from an *iterable of nested tuples and/or ints/entity instances*.

    Usage:
        pb = PackedBuilder()
        for obj in iterable:   # each obj can be a nested tuple or an int
            pb.add(obj)
        packed = pb.finish()   # PackedSequence representing (obj0, obj1, ...)
    """

    __slots__ = ("data", "struct", "model", "_top_level_count")

    def __init__(self, model=None, data_type_code="q", struct_type_code="I"):
        self.data = array(data_type_code)
        self.struct = array(struct_type_code)
        self._top_level_count = 0
        self.model = model

    def _build_node(self, obj) -> int:
        """
        Append the encoding for `obj` into data/struct.
        Returns the struct index where this node starts.
        """
        # Tuples: either compress as a single array node (pure ints) or
        # as a general tuple node with children.
        if isinstance(obj, tuple):
            # If this is a pure tuple-of-ints (and not empty), compress as one array node.
            all_int = len(obj) and all(isinstance(x, (int, ifcopenshell.entity_instance)) for x in obj)
            if all_int:
                offset = len(self.data)
                for x in obj:
                    if isinstance(x, ifcopenshell.entity_instance):
                        self.data.append(x.id())
                    else:
                        self.data.append(x)
                start = len(self.struct)
                self.struct.append(TAG_ARRAY)
                self.struct.append(len(obj))
                self.struct.append(offset)
                return start

            # General tuple: TAG_TUPLE, n_children, then children.
            start = len(self.struct)
            self.struct.append(TAG_TUPLE)
            self.struct.append(0)  # placeholder for n_children
            n_children = 0
            for child in obj:
                n_children += 1
                self._build_node(child)
            self.struct[start + 1] = n_children
            return start
        elif obj is None:
            start = len(self.struct)
            self.struct.append(TAG_NONE)
            return start

        # Bare int → TAG_SINGULAR_INT, offset
        offset = len(self.data)
        if isinstance(obj, ifcopenshell.entity_instance):
            self.data.append(obj.id())
        else:
            self.data.append(obj)
        start = len(self.struct)
        self.struct.append(TAG_SINGULAR_INT)
        self.struct.append(offset)
        return start

    def add(self, obj) -> None:
        """
        Add one top-level object from the input stream.
        Its node is appended to `struct` after any previous ones.
        """
        self._build_node(obj)
        self._top_level_count += 1
        return self

    def finish(self) -> "PackedSequence":
        return PackedSequence(self.data, self.struct, self._top_level_count, self.model)


class PackedSequence:
    """
    Read-only sequence over the packed representation.

    - `__len__` → number of top-level items (implicit outer tuple)
    - `__iter__` → yields Python values (ints or tuples)
    - `__getitem__(i)` → returns the i-th top-level item as int/tuple
    - `__getitem__(slice)` → materialises everything, then slices (tuple)
    """

    __slots__ = ("_data", "_struct", "_top_level_count", "_model", "_last_index",
        "_last_struct_pos",
        "_last_value",)

    def __init__(self, data: array, struct: array, top_level_count: int, model: Optional[ifcopenshell.file] = None) -> None:
        self._data = data
        self._struct = struct
        self._top_level_count = top_level_count
        self._model = model
        self._last_index = None
        self._last_struct_pos = None
        self._last_value = None

    def __len__(self) -> int:
        return self._top_level_count

    # ---- core decoder ----

    def _skip_subtree(self, idx: int) -> int:
        """
        Given an index into struct pointing at a node,
        return the index of the next node after its entire subtree.

        This does *not* allocate any Python tuples/ints.
        """
        tag = self._struct[idx]

        if tag == TAG_NONE:
            return idx + 1

        if tag == TAG_ARRAY:
            # TAG_ARRAY, length, offset
            return idx + 3

        if tag == TAG_SINGULAR_INT:
            # TAG_SINGULAR_INT, offset
            return idx + 2

        if tag == TAG_TUPLE:
            n = self._struct[idx + 1]
            j = idx + 2
            for _ in range(n):
                j = self._skip_subtree(j)
            return j

        raise ValueError(f"Unknown tag in struct: {tag!r}")

    def _decode_subtree(self, idx: int):
        """
        Decode one node starting at struct[idx].

        Returns: (python_value, next_idx)
          - python_value is int or (nested) tuple of ints/tuples
          - next_idx is the index in struct just after this subtree
        """
        tag = self._struct[idx]

        if tag == TAG_NONE:
            return None, idx + 1

        if tag == TAG_ARRAY:
            length = self._struct[idx + 1]
            offset = self._struct[idx + 2]
            value = tuple(self._data[offset + k] for k in range(length))
            return value, idx + 3

        if tag == TAG_TUPLE:
            n = self._struct[idx + 1]
            items = []
            j = idx + 2
            for _ in range(n):
                child_val, j = self._decode_subtree(j)
                items.append(child_val)
            return tuple(items), j

        if tag == TAG_SINGULAR_INT:
            offset = self._struct[idx + 1]
            value = self._data[offset]
            return value, idx + 2

        raise ValueError(f"Unknown tag in struct: {tag!r}")

    # ---- iteration & indexing ----

    def _to_model_instance(self, x):
        if self._model is None:
            return x
        elif isinstance(x, tuple):
            return tuple(self._to_model_instance(y) for y in x)
        else:
            return self._model[x]

    def __iter__(self):
        idx = 0
        for _ in range(self._top_level_count):
            value, idx = self._decode_subtree(idx)
            yield self._to_model_instance(value)

    def __getitem__(self, key):
        # Slicing: simplest is "materialise, then slice".
        if isinstance(key, slice):
            return self.to_tuple()[key]

        # Integer index: stream through until we hit that element.
        n = self._top_level_count
        idx = key
        if idx < 0:
            idx += n
        if idx < 0 or idx >= n:
            raise IndexError("index out of range")
        
        if idx == self._last_index:
            return self._last_value
        elif self._last_index is not None and idx > self._last_index:
            i = self._last_index + 1
            pos = self._last_struct_pos
        else:
            i = 0
            pos = 0

        while i < idx:
            # For all earlier elements, just skip structurally
            pos = self._skip_subtree(pos)
            i += 1

        if i == idx:
            value, next_pos = self._decode_subtree(pos)

            self._last_index = i
            self._last_struct_pos = next_pos
            self._last_value = value

            return self._to_model_instance(value)

        # Shouldn't reach here
        raise IndexError("index out of range")

    # ---- helpers ----

    def to_tuple(self):
        warnings.warn("Don't do this")
        """Materialise the implicit outer tuple."""
        return tuple(self)

    def __repr__(self) -> str:
        return f"PackedSequence({self.to_tuple()!r})"

def encode_nested_tuples(model: ifcopenshell.file, data:Sequence):
    builder = PackedBuilder(model=model)
    for val in data:
        builder.add(val)
    return builder.finish()

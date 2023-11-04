def replace_substrings(input_string, substrings_to_remove = ['.feature', '.ifc']):
    """ 
    This function is used to remove extensions.
    
    For example, if the input is 'ALB001_Alignment-in-spatial-structure.feature', the '.feature' extension will be removed.
    Similarly, if the input is 'fail-alb001-scenario01-contained_relation_not_directed_to_ifcsite.ifc', the '.ifc' extension will be removed.
    Option to add other substrings in 'substrings_to_remove'
    """
    for substring in substrings_to_remove:
        input_string = input_string.replace(substring, '')
    return input_string

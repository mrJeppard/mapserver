"""class obj that handles how to specify grouping and specification"""

"""
Notes:
Example:
    qstr = "Tissue==BLCA&&NPM_Mutation==1"
"""

ANDSTR="&&"
ISSTR="=="
GTSTR=">"
LTSTR="<"

class SubsetStr(object):
    """"""

    def __init__(self, str):
        self.str = str.strip()
        self.parse_str()
        
    def parse_str(self):
        arr = self.str.split(ANDSTR)

        self.tuple_list = map(lambda x: tuple(x.split(ISSTR)), arr)
        self._strs_to_float()

    def get_attrids(self):
        return [attrid for attrid, catid in self.tuple_list]

    def get_name(self):

        name = ""
        for attrid, catid in self.tuple_list:
            name += str(attrid) + ", " + str(catid) + " and "
        return name

    def db_query_string(self):
        """Makes a database query string from the groupspec query.
        this is what you were working on..."""
        qstr = ""
        running = False
        for attrid, catid in self.tuple_list:
            if running:
                qstr += " and "
            if catid is not None:
                try:
                    qstr += attrid + " == '" + catid +"'"
                except TypeError:
                    qstr += attrid + " == " + str(catid )
                    pass

            running = True

        return qstr

    def _strs_to_float(self):
        parsed = self.tuple_list
        # Use float conversion for the category id if possible.
        for i, group in enumerate(parsed):
            try:
                parsed[i] = (group[0], float(group[1]))
            # Has a value error if conversion isn't possible, and an index error
            # if there wasn't a category id to convert.
            except (ValueError, IndexError):
                    pass

        self.tuple_list = parsed


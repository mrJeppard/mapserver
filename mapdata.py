"""
This is a class for holding and interacting with "map data."
Map data is a set of x-y positions and attributes associated with
"""

import pandas as pd
import numpy as np
from sklearn.metrics import calinski_harabaz_score
from subsetstr import SubsetStr

def is_str(thing):
    return isinstance(thing, basestring)

def get_xys(mapid="Pancan12-mRNA"):
    import datapointer
    xyfilename = datapointer.xys[mapid]
    return pd.read_table(xyfilename,index_col=0)

def get_attrid_list(mapid="Pancan12-mRNA"):
    import datapointer
    attrfilename = datapointer.attrs[mapid]
    return pd.read_table(attrfilename, index_col=0, nrows=1).columns.tolist()

def get_attr(mapid="Pancan12-mRNA", attrid=None):
    """Return a pandas Series."""
    attrlist = ["Nodes"] #index column name
    # Produce same behavior if a single attribute is given.
    attrlist = attrlist.append(attrid)

    import datapointer
    attrfilename = datapointer.attrs[mapid]
    return pd.read_table(attrfilename, index_col=0, usecols=attrlist)[attrid]

def get_attrs(mapid="Pancan12-mRNA", attrid_list=None):

    # Index column name must be "Nodes"
    index_col = ["Nodes"]
    index_col.extend(attrid_list)
    attrid_list = index_col

    import datapointer
    attrfilename = datapointer.attrs[mapid]
    return pd.read_table(attrfilename, index_col=0, usecols=attrid_list)

def stitch(xys, attrs):
    return pd.concat([xys, attrs], axis=1)

def subset(table, qstr):
    return table.querry(qstr)

def group_by(table, attrid):
    table.groupby(attrid)

def attr_dtype(mapid, attrid):
    """Return one of 'bin', 'cat', or 'cont'"""
    attr = get_attr(mapid, attrid)
    dtype_ = attr.dtype

    if dtype_ == 'object':
        if len(attr.unique()) == 2:
            return 'bin'
        else:
            return 'cat'
    elif len(attr.unique()) == 2:
        return 'bin'
    else:
        return 'cont'

def attr_is_cat_bin(mapid, attrid):
    dtype_ = attr_dtype(mapid, attrid)
    return dtype_ == 'cat' or dtype_ == 'bin'

#########################################333
#attr hierarchy
def make_attr_hierarcy(mapid):

    attr_hierarchy = {}

    #the remaining subsets to explore
    subset = [None]
    all_attrids = MapData(mapid).get_all_attrids()
    while len(subset):
        subset_str = subset.pop()
        map_data = MapData(mapid)
        map_data.set_attrs(all_attrids)
        map_data.set_subset(subset_str)
        if map_data._nrows() < 20:
            continue

        next_group = map_data.attr_with_max_ch()
        attr_hierarchy[subset_str] = next_group
        if next_group is None:
            continue

        for catid in map_data.get_catids(next_group):
            if subset_str is None:
                next_sub = next_group + "==" + catid
            else:
                next_sub = subset_str + "&&" + next_group + "==" + catid

            subset.append(next_sub)

    return attr_hierarchy

#########################################333

class MapData(object):
    """
    This this this
    """

    def __init__(self, mapid="Pancan12-mRNA"):
        self.mapid = mapid
        self.grouped = False
        self.table = get_xys(mapid)
        self.subset = ""
        self.subsetted = False

    def get_table(self):
        return self.table

    def get_all_attrids(self):
        return get_attrid_list(self.mapid)

    def set_attrs(self, attrids):
        """"""
        self.attrids = attrids
        self.table = stitch(self.table, get_attrs(attrid_list=attrids))

    def set_attrs_from_subset(self, subset_str):
        self.set_attrs(SubsetStr(subset_str).get_attrids())

    def set_space_subset(self, qstr):
        self.table = self.table.query(qstr)

    def set_subset(self, subset_str):
        if subset_str is None:
            return None
        self.subsetted = True
        self.subset = subset_str
        self.SubsetObj = SubsetStr(subset_str)
        qstr = self.SubsetObj.db_query_string()
        self.table = self.table.query(qstr)

    def set_group_table(self, attrid):
        if attrid is None:
            return None
        self.grouped = True
        pd_groupby = self.table.groupby(by=[attrid])
        means = pd_groupby.mean()
        means["Size"] = pd_groupby.size()
        means.dropna(inplace=True)
        self.group_table = means

    def get_names(self):
        if not self.grouped:
            return self.table.index.tolist()
        else:
            col = self.group_table.index.name
            catids = self.group_table.index.tolist()
            if self.subsetted:
                prefix = self.SubsetObj.get_name()
            else:
                prefix = ""
            return [prefix + col + ", " + catid for catid in catids]
    def get_name_from_subset(self):
        return self.SubsetObj.get_name()[:-4]

    def get_subsets(self):
        old_subset = self.subset
        if not self.grouped:
            return None
        else:
            catids = self.group_table.index.tolist()
            prefix = self.group_table.index.name
            if self.subsetted:
                return [old_subset + "&&" + prefix +"=="+ catid for catid in catids]
            else:
                return [prefix +"==" + catid for catid in catids]

    def attr_with_max_ch(self):
        """
        Returns the attribute id with the maximum Calinski-Harabasz score.
        These scores are computed with the subset of leaves specified by the
        group specification argument.
        :return: (str or None) - An attribute identifier or None if no valid
        CH indices were available.
        """
        calinski_harabaz_scores = self._ch_scores()

        # If we have no good CH indecies than we return None.
        if calinski_harabaz_scores is None or calinski_harabaz_scores.max() == -1:
            return None
        return calinski_harabaz_scores.idxmax()

    def get_group_table(self):
        return self.group_table


    def _nrows(self):
        return self.table.shape[0]

    def _ch_scores(self):
        # Require a large percentage of data so the rank of the CH indecies has
        # a high level of confidence
        fraction_needed = .8
        nrows = self._nrows()
        required = nrows * fraction_needed
        ch_measures = []

        # The CH index only makes sense for binary or categorical attributes.
        # Filter all the given attributes down to categorical and binary ones.
        catbin_attrs = self._cat_bin_attrids()

        for attrid in catbin_attrs:
                # Reduce the vector to attribute values
                attr = self.table[attrid].dropna()
                # Reduce the x-y pairs to those the attribute has values for.
                xys = self.table.loc[attr.index, ['x', 'y']]

                try:

                    if xys.shape[0] < required:
                        # Signify there is not a valid CH index.
                        raise ValueError
                    else:
                        ch_score = calinski_harabaz_score(xys, attr)
                # Value errors occur when the number of categories is only 1,
                # in which case we need to signify we don't have a valid CH index.
                except ValueError:
                    ch_score = -1

                ch_measures.append(ch_score)

        # Return a pandas Series that is labeled with the attribute names.
        return pd.Series(ch_measures, index=catbin_attrs)

    def _cat_bin_attrids(self):
        attrids = self.attrids
        cat_bin_attrid = [attrid for attrid in attrids
                          if attr_is_cat_bin(self.mapid, attrid)
                          ]

        return cat_bin_attrid

    def get_catids(self, attrid):
        return self.table[attrid].dropna().unique().tolist()

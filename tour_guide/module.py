import pandas as pd


def reduce_categories(data_path):
    '''Given a path to a categories csv with the appropriate columns,
    produces a data frame including only those Yelp categories that
    are used on neighborhoods.com

    data_path (str): The file path to a yelp categories csv.
    '''

    data = pd.read_csv(data_path)

    data.columns = ['alias', 'parents', 'title', 'name', 'urban_distance',
                    'suburban_distance', 'neighborhood', 'amenities', 'bard']

    no_neighborhood_indices = data.neighborhood == "N"
    no_amenities_indices = data.amenities == "N"
    no_bard_indices = data.bard == "N"

    used_indices = ~ (no_neighborhood_indices
                      & no_amenities_indices
                      & no_bard_indices)

    data = data.loc[used_indices]

    neighborhood_nan_indices = data.neighborhood.isnull()
    amenities_nan_indices = data.amenities.isnull()
    bard_nan_indices = data.bard.isnull()

    data.loc[neighborhood_nan_indices, 'neighborhood'] = 'Y'
    data.loc[amenities_nan_indices, 'amenities'] = 'Y'
    data.loc[bard_nan_indices, 'bard'] = 'Y'

    name_nan_indices = data.name.isnull()
    data.loc[name_nan_indices, 'name'] = data.loc[name_nan_indices, 'alias']

    return data.reset_index(drop=True)


def create_map(reduced_data):
    '''Takes a data frame produced by reduced_categories() and outputs a
    mapping between neighborhoods.com display categories and yelp
    categories.

    reduced_data (dataframe): A pandas data frame produced by
    reduced_categories().
    '''

    category_map = {}
    for name in set(reduced_data['name']):
        temp = reduced_data[reduced_data['name'] == name]
        yelp_categories = set(temp['alias'])
        category_map[name] = list(yelp_categories)

    return category_map

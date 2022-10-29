# As a user, I want to clean my DataFrame such that it is ready for clustering
# As a user, I want to be able to choose wheter or not applying a dimension reduction algorithm
# As a user, I want to be able to choose between multiple clustering algorithms
# As a user, I want to be able to cluster my DataFrame
# As a user, I want to be able to retrieve my results

from cleaner import cleaner
from sklearn.decomposition import PCA


class Clustering_Pipeline:
    """
    Class that cleans a DataFrame and apply clustering to it"""

    def __init__(
        self,
        df: pd.DataFrame,
        dimension_reduction_method: str,
        dimension_number: int,
        clustering_algorithm: str,
        cluster_number: int,
    ):
        self.df = df
        self.dr = dimension_reduction_method
        self.ca = clustering_algorithm
        self.dn = dimension_number
        self.cn = cluster_number
        assert self.dr in [
            "None",
            "PCA",
        ], "La méthode de réduction de dimension doit être None ou une PCA"
        assert self.ca in ["KMeans"], "La méthode de clustering doit être KMeans"

    def cleaning_df(self) -> pd.DataFrame:
        cleaning = DataFrame_cleaning(self.df)
        self.df = cleaning.global_cleaner()
        self.df = self.df[["price", "surface", "localisation", "nombre_pieces", "rue"]]
        self.df = pd.get_dummies(self.df, columns=["localisation", "rue"])

        return self.df

    def reduction_dimension(self) -> pd.DataFrame:
        dict_dr = {"PCA": PCA(n_components)}
        if self.dr == "None":
            pass
        else:
            model = dict_dr[self.dr]
            self.df = pd.DataFrame(model.fit_transform(df))
        return self.df

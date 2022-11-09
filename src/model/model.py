import sys
import yaml
from yaml.loader import SafeLoader
import os

current_path = os.getcwd()
with open(os.path.join(current_path, "src/model/model_params.yaml"), "r") as f:
    data = list(yaml.load_all(f, Loader=SafeLoader))[0]

sys.path.append(os.path.join(current_path, "src/cleaner"))

from cleaner import *
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


class Clustering_Pipeline:
    """
    Class that cleans a DataFrame and apply clustering to it"""

    def __init__(
        self,
        df: pd.DataFrame,
    ):  
        self.df = df
        self.df_original=df
        self.df_original = df
        self.dr = data["dimension_reduction_method"]
        self.ca = data["cluster_model"]
        self.dn = data["nb_dimension"]
        self.cn = data["nb_cluster"]
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
        dict_dr = {"PCA": PCA(n_components=self.dn)}
        if self.dr == "None":
            pass
        else:
            model = dict_dr[self.dr]
            self.df = pd.DataFrame(model.fit_transform(self.df))
        return self.df

    def clustering(self) -> pd.DataFrame:
        dict_cl = {"KMeans": KMeans(n_clusters=self.cn)}
        model = dict_cl[self.ca]
        model.fit(self.df)
        self.df_original["labels_predicted"] = model.labels_
        if "Unnamed: 0" in self.df_original.columns:
            self.df_original.drop("Unnamed: 0", axis=1, inplace=True)
        return self.df_original

    def full_pipeline(self):
        self.df=self.cleaning_df()
        self.df.to_csv("quemierda.csv",index=False)
        self.df=self.reduction_dimension()
        self.df=self.clustering()

        return self.df

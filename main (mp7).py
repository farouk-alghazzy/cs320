from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LogisticRegression

class UserPredictor:
    def __init__(self):
        self.model = Pipeline([
                             ("pf", PolynomialFeatures(degree=2, include_bias=False)),
                             ("std", StandardScaler()),
                             ("lr", LogisticRegression(fit_intercept=False)),
                              ])
        
    def schmooze(self, user, log):
        train_simple = user
        log = log[log["url"] == "/laptop.html"]
        self.laptop_dict = {}
        self.badge_dict = {}
        
        for user in log.itertuples():
            user_id = user.user_id
            if user_id not in self.laptop_dict:
                self.laptop_dict[user_id] = user.seconds
            else:
                self.laptop_dict[user_id] += user.seconds
           
        for user in train_simple.itertuples():
            user_id = user.user_id
            if user_id not in self.laptop_dict:
                train_simple.at[user.Index, "laptop_seconds"] = 0
            else:
                train_simple.at[user.Index, "laptop_seconds"] = self.laptop_dict[user_id]
                
        for user in train_simple.itertuples():
            user_id = user.user_id
            badge = user.badge
            if badge == "gold":
                self.badge_dict[user_id] = 3
            elif badge == "silver":
                self.badge_dict[user_id] = 2
            elif badge == "bronze":
                self.badge_dict[user_id] = 1
            else:
                self.badge_dict[user_id] = 0 
                
        for user in train_simple.itertuples():
            user_id = user.user_id
            if user_id not in self.badge_dict:
                train_simple.at[user.Index, "badge_int"] = 0
            else:
                train_simple.at[user.Index, "badge_int"] = self.badge_dict[user_id]      
        return train_simple
        
    def fit(self, user, log, click):
        train_simple = self.schmooze(user, log)
        xcols = ["age",  "past_purchase_amt", "laptop_seconds", "badge_int"]
        ycol = "y"
        self.model.fit(train_simple[xcols], click[ycol])

    def predict(self, user, log):
        test_df = self.schmooze(user, log)
        xcols = ["age", "past_purchase_amt", "laptop_seconds", "badge_int"]
        return self.model.predict(test_df[xcols])
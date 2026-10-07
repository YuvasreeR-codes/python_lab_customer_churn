import pickle

# 1. Load the model file
with open('tree_churn.pkl', 'rb') as file:
    model = pickle.load(file)

# 2. Print the features
if hasattr(model, 'feature_names_in_'):
    print("Features used by the model:")
    for feature in model.feature_names_in_:
        print(f" - {feature}")

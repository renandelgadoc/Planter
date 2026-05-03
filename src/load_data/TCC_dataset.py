import os
import pandas as pd

def load_data(num_features, data_dir):
    data_dir = data_dir + "/TCC/"
    feat_path = os.path.join(data_dir, "selected_features.txt")
    x_train_path = os.path.join(data_dir, "X_train.csv")
    y_train_path = os.path.join(data_dir, "y_train_bin.csv")
    x_test_path  = os.path.join(data_dir, "X_test.csv")
    y_test_path  = os.path.join(data_dir, "y_test_bin.csv")

    # ---- features ----
    with open(feat_path, "r") as f:
        used_features = [line.strip() for line in f]

    # used_features = used_features[:num_features]
    # used_features = used_features[:num_features]
    
    used_features=["dsport","sttl","smeansz","ct_dst_src_ltm","sport","dmeansz","dttl","trans_depth","proto","Spkts","dwin"][:num_features]
    print(used_features)

    # ---- carregar X como DataFrame ----
    X_train = pd.read_csv(x_train_path)
    X_test  = pd.read_csv(x_test_path)

    # Select only those columns
    X_train = X_train[used_features]
    X_test = X_test[used_features]

    # ---- carregar Y como NUMPY ARRAY ----
    y_train = pd.read_csv(y_train_path, skiprows=1, header=None).iloc[:, 0].astype(int).to_numpy()
    y_test  = pd.read_csv(y_test_path,  skiprows=1, header=None).iloc[:, 0].astype(int).to_numpy()

    # print(y_train[:10])
    # print(y_test[:10])
    # print(X_train[:10])
    # print(X_test[:10])
    
    return X_train, y_train, X_test, y_test, used_features


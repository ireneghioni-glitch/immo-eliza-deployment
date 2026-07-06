from sklearn.model_selection import train_test_split


# --- Constants ---------------------------------------------------------------------------------------

# features train/test sets paths
X_TRAIN_RAW_CSV_PATH = "../data/raw/train_test/X_train_raw.csv"
X_TEST_RAW_CSV_PATH = "../data/raw/train_test/X_test_raw.csv"
# target train/test sets paths
Y_TRAIN_CSV_PATH = "../data/raw/train_test/y_train.csv"
Y_TEST_CSV_PATH = "../data/raw/train_test/y_test.csv"


# --- Functions ---------------------------------------------------------------------------------------


def split_data(df):
    # first splitting of dataset: Target & Features
    # target y -> 'price'
    # fature X -> all the other columns except 'price_area_m2'
    X, y = df.drop(columns=['price', 'price_per_m2']), df['price']

    # second splitting of dataset: Train and Test sets
    # split 80/20
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.2)

    # saving splitted sets

    # X_train_raw contains 80% of rows with row data (numbers and strings)
    X_train_raw.to_csv(X_TRAIN_RAW_CSV_PATH, index=False)

    # X_test_raw contains 20% of rows with row data invisible to the model before final test
    X_test_raw.to_csv(X_TEST_RAW_CSV_PATH, index=False)

    # y_train contains 80% of rows with target data (price, numeric)
    y_train.to_csv(Y_TRAIN_CSV_PATH, index=False)

    # y_test contains 20% of rows with target data (price, numeric)
    y_test.to_csv(Y_TEST_CSV_PATH, index=False)

    return X_train_raw, X_test_raw, y_train, y_test
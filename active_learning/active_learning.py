import os

import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.preprocessing import scale
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, confusion_matrix

class ActiveLearning(object):
    def __init__(self, labels, feature_file, data_dir, amount_to_label=10):
        self.labels = labels
        self.feature_file = feature_file
        self.data_dir = data_dir
        self.amount_to_label = amount_to_label
        self.validation = None

        # Load feature file
        self.data = pd.read_csv(feature_file)
        self.data.drop_duplicates(subset="filename")

        # Make transformations to the features
        features = self.data.columns[:-2]
        self.data[features] = self.data[features].apply(scale)
        self.data[features] = self.data[features].apply(np.negative)
        self.data[features] = self.data[features].apply(np.exp)

        # Strip folders from filename
        self.data["filename"] = self.data["filename"].apply(lambda x: os.path.join(self.data_dir, os.path.basename(x)))

        # Initialize the classifier
        self.model = LogisticRegression(
            penalty='l2',
            C=.01,
            class_weight="balanced",
            random_state=None,
            n_jobs=-1,
            warm_start=False,
            fit_intercept=True
        )

        self.labeled_flights = dict()

    def load_validation(self, filename):
        self.validation = pd.read_csv(filename)
        rename = {"label": {name: idx for idx, name in enumerate(self.labels)}}
        self.validation.replace(rename, inplace=True)

        tmp = self.data.loc[self.data["filename"].isin(self.validation["filename"])]
        for idx, row in tmp.iterrows():
            new_value = list(self.validation["label"].loc[self.validation["filename"] == row["filename"]])[0]
            tmp.set_value(idx, "label", new_value)
        self.validation = tmp

        self.data = self.data.loc[~self.data["filename"].isin(self.validation["filename"])]


    def restart(self):
        self.labeled_flights = dict()
        self.model = clone(self.model)

    def save_to_csv(self, filename):
        fn, lbl = self.get_labeled_training()
        lbl = [self.labels[l] for l in lbl]
        data = pd.DataFrame({"filename": fn, "label": lbl})
        data.to_csv(filename, index=False)

    def load_from_csv(self, filename):

        try:
            data = pd.read_csv(filename)
            self.labels = list(data["label"].unique())
            lbl_idx = {lbl: i for i, lbl in enumerate(self.labels)}

            self.labeled_flights = dict()
            for _, row in data.iterrows():
                self.labeled_flights[row["filename"]] = lbl_idx[row["label"]]

            return True
        except:
            return False

    def get_label_names(self):
        return self.labels[:]

    def set_label_names(self, labels):
        self.labels = labels[:]

    def label_flights(self, new_labels):
        # Update labels
        for flight, label in new_labels:
            self.labeled_flights[flight] = label

    def get_centroids(self):
        # Identifying centroids
        train_data = self.data.drop(["label", "filename"], axis=1)
        train_labels = list(self.data["label"].astype(int))

        model = clone(self.model)
        model.fit(train_data, train_labels)

        # Predicted probability for each instance
        probs = model.predict_proba(train_data)

        # Sort flights of each cluster by probability
        num_clusters = len(self.data['label'].unique())
        sorted_probs = [[] for i in range(num_clusters)]
        for i, prob in enumerate(probs):
            sorted_probs[train_labels[i]].append((i, prob[train_labels[i]]))
        for i in range(num_clusters):
            sorted_probs[i] = sorted(sorted_probs[i], key=lambda x: x[1])

        # Get centroids
        centroids = []
        file_names = list(self.data["filename"])
        for cluster, l in enumerate(sorted_probs):
            centroid = file_names[l[-1][0]]
            centroids.append(centroid)

        return centroids

    def reset_model(self):
        self.model = clone(self.model)
        self.labeled_flights = dict()

    def get_flights_to_label(self):
        # Create version of data with the labels given by user
        data_with_labels = self.data.copy()

        # Add labels to the data
        data_with_labels["label"] = -1
        for filename, label in self.labeled_flights.items():
            data_with_labels.loc[data_with_labels["filename"] == filename, "label"] = label

        # Separate into training and test
        train = data_with_labels.loc[data_with_labels["filename"].isin(self.labeled_flights.keys())].copy()
        train_labels = train["label"]
        train.drop(["label", "filename"], axis=1, inplace=True)
        test = data_with_labels.loc[~data_with_labels["filename"].isin(self.labeled_flights.keys())].copy()
        test_filenames = list(test["filename"])
        test.drop(["label", "filename"], axis=1, inplace=True)

        # Train model with the new labeled data
        self.model.fit(train, train_labels)

        # Get and sort probabilities for the test data
        probs = self.model.predict_proba(test)
        return self._select_flights(probs, test_filenames)

    def _select_flights(self, probabilities, file_names):
        sorted_probs = [[np.max(p), np.argmax(p), file_names[i]] + list(p) for i, p in enumerate(probabilities)]
        sorted_probs = sorted(sorted_probs)

        num_uncertain = int(np.ceil(self.amount_to_label / 2.0))
        num_almost_labeled = self.amount_to_label - num_uncertain

        # # First, get the most uncertain
        selected = [x[2] for x in sorted_probs[:num_uncertain]]

        # Now, get the labels and find out which has the fewest number of instances
        labels = [x[1] for x in sorted_probs]
        label_fewest = np.argsort(np.bincount(labels))[0]

        # Reduce to unselected instanced not assigned to that label, sort by probability of that label and pick
        # the ones with highest probability (almost classified as that label)
        reduced = sorted_probs[len(selected):]
        reduced = [x for x in reduced if x[1] != label_fewest]
        reduced = sorted(reduced, key=lambda x: x[3 + label_fewest], reverse=True)
        selected = selected + [x[2] for x in reduced[:num_almost_labeled]]

        return selected

    def get_labeled_training(self):
        return tuple(zip(*self.labeled_flights.items()))

    def get_labeled_test(self, sorted=True, reverse=True):
        # Create version of data with the labels given by user
        data_with_labels = self.data.copy()

        # Add labels to the data
        data_with_labels["label"] = -1
        for filename, label in self.labeled_flights.items():
            data_with_labels.loc[data_with_labels["filename"] == filename, "label"] = label

        # Separate into training and test
        train = data_with_labels.loc[data_with_labels["filename"].isin(self.labeled_flights.keys())].copy()
        train_labels = train["label"]
        train.drop(["label", "filename"], axis=1, inplace=True)
        test = data_with_labels.loc[~data_with_labels["filename"].isin(self.labeled_flights.keys())].copy()
        test_filenames = np.asarray(test["filename"])
        test.drop(["label", "filename"], axis=1, inplace=True)

        # Train model with the new labeled data
        self.model.fit(train, train_labels)
        test_labels = self.model.predict(test)
        test_proba = self.model.predict_proba(test)
        test_proba = [max(p) for p in test_proba]
        order = np.argsort(test_proba)
        if reverse:
            order = order[::-1]

        if sorted:
            test_filenames = test_filenames[order]
            test_labels = test_labels[order]

        if self.validation is not None:
            val_data = self.validation.drop(["filename", "label"], axis=1)
            true_lbls = self.validation["label"].astype(int)
            pred_lbls = self.model.predict(val_data)
            # print(f1_score(true_lbls, pred_lbls, average="macro"))
            print(confusion_matrix(true_lbls, pred_lbls))

        return test_filenames, test_labels

    def get_label_distribution(self):
        _, test_labels = self.get_labeled_test()
        _, training_labels = self.get_labeled_training()
        all_labels = list(training_labels) + list(test_labels)

        return np.bincount(all_labels)

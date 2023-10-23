from BrainQbrain_application import HospitalProgram, ClinicProgram
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split 
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
import numpy as np
import logging
from squidasm.run.stack.run import run
from squidasm.sim.stack.common import LogManager
from squidasm.run.stack.config import StackNetworkConfig


number_of_patients = 20
number_of_sensors =  10

# Create a simulated dataset for the nv center defect quantum sensors
X, y = make_classification(
    n_samples=number_of_patients, 
    n_features=2 * number_of_sensors, n_informative=20, 
    n_redundant=0, n_clusters_per_class=1, 
    class_sep=2.0, random_state=2)

# Map features into qubits' phi and theta 
for i in range(X.shape[1]//2):
    col_phi = X[:, 2*i]
    phi = 2 * np.arccos(col_phi / max(abs(col_phi)))
    col_theta = X[:, 2*i+1]
    theta = np.arccos(col_theta / max(abs(col_theta)))
    X[:, 2*i] = phi
    X[:, 2*i+1] = theta

# Create a network configuration
# cfg = create_two_node_network(node_names=["Hospital", "Clinic"])
cfg = StackNetworkConfig.from_file("BrainQbrain.yaml")

# Create instances of programs to run
Clinic_program = ClinicProgram(X)
Hospital_program = HospitalProgram()

# toggle logging. Set to logging.INFO for logging of events.
Clinic_program.logger.setLevel(logging.ERROR)
Hospital_program.logger.setLevel(logging.ERROR)

# Run the simulation. Programs argument is a mapping of network node labels to programs to run on that node
_, X_received = run(
    config=cfg,
    programs={"Hospital": Hospital_program, "Clinic": Clinic_program},
    num_times=1,
)

# print(f"State to teleport:\n{sender_result}")
# print(f"State received:\n{X_received[0]['final_probs']}")

# Map the extracted data from qubits for training
X_received = np.reshape(X_received[0]['final_probs'], (number_of_patients,-1))

# Split the dataset in confirmed patients and new patients
X_train, X_test, y_train, y_test = train_test_split(
    X_received, y , random_state=104, test_size=0.25, shuffle=True) 

# We create a list of classifiers with their names
classifiers = [
    ('Logistic Regression', LogisticRegression()),
    ('Support Vector Machine', SVC()),
    ('KNN', KNeighborsClassifier()),
    ('Random Forest', RandomForestClassifier()),
    ('Naive Bayes', GaussianNB())
]

# Train and evaluate each classifier
for name, clf in classifiers:
    # Fit the classifier on the training data
    clf.fit(X_train, y_train)
    # Predict on the test data
    y_pred = clf.predict(X_test)
    # Compute the F1 score, precision and recall scores
    f1 = f1_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    # Print the results
    print(f'{name} F1 score: {f1:.2f}, precision: {prec:.2f}, recall: {rec:.2f}')

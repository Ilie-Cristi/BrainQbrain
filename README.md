# BrainQbrain
### A quantum brain over the quantum internet

Nitrogen-vacancy (NV) nanodiamonds are materials with outstanding properties for quantum sensing: they can detect magnetic, electric, temperature and pressure fields at the nanometer level, using luminescence and optical magnetic resonance of NV centers.They have a stable electronic spin and can be manipulated and read optically, using laser light and a photon detector. A major advantage of NV nanodiamonds is that they can operate at room temperature, unlike other quantum systems that require cryogenic conditions. NV nanodiamonds have been used to measure the spin noise of transition metal paramagnetic nanoparticles such as rubidium, cobalt, and iron. They have also been used to detect the chemical functionality of surfaces by covalently binding target molecules to nanodiamonds. For this reason, an emerging direction of research is high-resolution neuroimaging.

The project is intended for use in a network of medical clinics for the diagnosis of early symptoms, or for the monitoring of neural disorders with the help of quantum sensors.

In the context of the development of a metropolitan, or even national quantum internet network, this project becomes a feasible application due to the fact that the computing resources, respectively the main quantum processing unit, can be located in a central hospital. Sensors can communicate through the quantum teleportation protocol directly with this central unit, not requiring complex circuits that require high complexity.


## Application

The application simulates the neural activity of patients through a locally generated data set that can be binary classified. We can choose within the source code BrainQbrain_run.py the number of sensors (diamonds with NV defect), as well as the number of patients.

The simulated data set can represent an average neural activity over a time interval, with the specification that time series can provide a more appropriate overview.

I later transposed two independent characteristics into the angles that describe the state of a qubit, phi and theta. We performed the process for each patient.

Once the data set with the qubit states is created, we use the quantum teleportation protocol to accurately transmit a high-resolution image of the mental activity.

In the simulation, I transmitted the entire data set by teleporting each qubit, later I divided it for training and testing. For the training subset we proposed a series of patients who were already diagnosed as healthy or having a mental illness X, and the testing subset will exemplify the new patients tested in the clinics.

For the classification we used a series of models and observed a good resistance even in real conditions (noisy qubits and noisy channel).

For further development, I will consider the use of time series that will provide me with a significantly greater amount of information about neural activity, as well as the use in the central hospital of quantum optimization algorithms for machine learning.


## Usage

Install the requirements.txt:

`pip install -r requirements.txt`

Note: for SQUIDasm a netsquid account will be needed. For more details you can see the SQUIDasm github page.
Make sure you have your SQUIDasm folder inside the project.

Modify the BrainQbrain_run.py file to specify the number of sensors and the number of patients.

Note: One qubit will be used for each sensor, multiplied with the number of patients, you will need to specify the number of qubits for the nv_device in the yaml config file.

Run the application:

`python3 BrainQbrain.py`

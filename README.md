![Icon Russell](resources/logo/Russell.png)

# Russell

Automatic synchronization of angiographic frames acquired with and without contrast medium is a crucial step for accurately pairing images corresponding to the same phase of the cardiac cycle, regardless of patient variability, acquisition angle, or video quality.

The identification of Coronary Artery Calcifications (CAC) in 2D Coronary Angiography (2DCA) images is clinically significant, yet often challenging due to motion artifacts and the intrinsic difficulty of visual interpretation.

This project introduces a method for synchronizing angiographic sequences with and without contrast enhancement in the absence of ECG signals during acquisition. The proposed approach relies on estimating the Euclidean distance between consecutive frames to generate an “ECG-like” signal capable of capturing cardiac periodicity and identifying corresponding phases of the cardiac cycle.

# Install

```dockerfile
docker build -t Russell .
docker run -d Russell
```

# Dataset
An example dataset is provided in the Resources folder.
To analyze your own datasets, add the corresponding information to the Dataset.xlsx file following the format shown in the provided example.

# Demo

```powershell
curl -i ^
  -H "Accept: application/json" ^
  -H "Content-Type: application/json" ^
  -X GET "http://localhost:4200/patients/Paz_001_01"```

Federated Learning Training System PRD

1. Overview of Requirements

This system aims to provide machine learning researchers with a complete federated learning experiment platform, supporting both offline federated learning and online federated learning modes. The system is implemented through command-line interaction, with core functions including offline federated learning training, online distributed training, parameter sweep experiment management, and training result recording and analysis. Users can conduct distributed model training while protecting data privacy and verify the effectiveness of different federated learning strategies.

2. Basic Functional Requirements

2.1 Offline Federated Learning Training Management

- Provide command-line parameter configuration interface, supporting hyperparameter settings such as client quantity, training rounds, local training rounds, learning rate, etc.
- Support two training modes: full client participation mode (all 20 clients participate every round) and partial client participation mode (randomly selecting 5/10/15 clients).
- Display dynamic progress prompts during training execution (e.g., "Round 3/10, Client 5/20 training..."), supporting interrupt operations (users can terminate training by entering Ctrl+C).
- Return training status (success/failure), with specific reasons output for failures (such as data loading failure, model saving error, insufficient memory).
- Automatically save training logs, containing test loss, accuracy, best model saving status for each training round.
- Data source supports pre-split MNIST dataset (pickle format), with each client having an independent data subset.

2.2 Online Federated Learning Distributed Training

- Implement server-client communication architecture based on TCP Socket, supporting multiple client concurrent connections.
- Server responsible for global model initialization, parameter aggregation (FedAvg algorithm), model distribution; clients responsible for local model training.
- Support user configuration of network parameters: receiving port, sending port, client quantity, training rounds, local training rounds.
- Provide connection status monitoring, displaying client connection status (e.g., "Client 3 connected, 5/10 clients ready").
- Support training process visualization, displaying aggregation progress, model performance metrics in real-time.
- Automatically handle network anomalies, providing connection failure retry mechanism and error recovery functions.

2.3 Parameter Sweep Experiment Management

- Support batch execution of experiments with different parameter combinations, including client quantity (5/10/20), training rounds (10), local training rounds (5/10).
- Provide one-click execution script, automatically running experiments for all parameter combinations.
- Experiment results automatically categorized and stored, with each experiment generating independent log files (e.g., "result_10_10_10.log").
- Support experimental comparative analysis, enabling comparison of model performance under different parameter settings.
- Provide experiment status query function, displaying lists of executing and completed experiments.

2.4 Model Training and Evaluation

- Support MLP neural network architecture training, with input layer 784-dimensional (28×28 pixels), hidden layers 256→128-dimensional, output layer 10-dimensional (MNIST classification).
- Provide model performance evaluation function, calculating accuracy, loss and other metrics on unified test set.
- Support model saving and loading, automatically saving the best performing model.
- Provide training process monitoring, recording loss changes, gradient information for each round.
- Support model visualization analysis, enabling viewing of model parameter distribution, gradient flow and other information.

3. Technical Specifications

3.1 System Architecture

- Programming Language: Python 3.x
- Deep Learning Framework: PyTorch
- Network Communication: Socket TCP/IP
- Data Processing: NumPy, TorchVision
- Logging System: Loguru

3.2 Model Configuration

- Network Type: Multilayer Perceptron (MLP)
- Optimizer: SGD (Stochastic Gradient Descent)
- Loss Function: Cross-Entropy Loss
- Activation Function: ReLU
- Batch Size: 32

3.3 Data Specifications

- Dataset: MNIST Handwritten Digit Dataset
- Data Format: Pre-split pickle files
- Client Quantity: 20 independent data subsets
- Test Set: Unified MNIST test set

4. Command-Line Interaction and Result Presentation

4.1 Main Interface Interaction

- Main interface adopts menu-style interaction, containing function options: [1] Offline Federated Learning [2] Online Federated Learning [3] Parameter Sweep Experiment [4] View Training Logs [5] Model Evaluation [6] Exit.
- User input requires validity verification (e.g., options must be numbers 1-6, parameter values must be within reasonable range), displaying Chinese prompts for erroneous input.
- Support parameter configuration wizard, guiding users to set training parameters.

4.2 Result Presentation

- When generating analysis results, users can choose whether to display training metrics using tabular text format.
- Support training process visualization, displaying loss curves, accuracy change charts, etc.
- All output results support saving as TXT files (users can specify save path), files must contain training parameters, performance metrics, model information and tabular text.

4.3 Log Management

- Automatically generate training log files, containing timestamps, training parameters, performance metrics.
- Support log query function, enabling filtering of historical records by time, parameter combinations.
- Provide log analysis tools, supporting batch log processing and result summarization.
import wandb
YOUR_WANDB_USERNAME = "gefen_and_tomer"
project = "nlp_project"

command = [
        "${ENVIRONMENT_VARIABLE}",
        "${interpreter}",
        "StrategyTransfer.py",
        "${project}",
        "${args}"
    ]

sweep_config = {
    "name": "oracle strategy set to 0 - e new incorporate strategies on test set - partial",
    "method": "grid",
    #"metric": {
    #    "goal": "maximize",
    #    "name": "AUC.test.max"
    #},
    "parameters": {
        "seed": {"values": list(range(1, 6))},

        # aggressive pursuit hyperparameters on validation set
        # "ENV_HPT_mode": {"values": [True]},
        # "basic_nature": {"values": [19]},
        # "aggressive_pursuit_fixed_interval": {"values": [1, 2, 3]},
        # "aggressive_pursuit_divisor": {"values": [2, 3]},

        # adaptive strategy hyperparameters on validation set
        # "ENV_HPT_mode": {"values": [True]},
        # "basic_nature": {"values": [20]},
        # "adaptive_learning_disappointment_threshold": {"values": [0.2, 0.3, 0.4, 0.5, 0.6]},

        # conservative strategy hyperparameters on validation set
        # "ENV_HPT_mode": {"values": [True]},
        # "basic_nature": {"values": [18]},
        # "conservative_strategy_initial_threshold": {"values": [0.4, 0.5]},
        # "conservative_strategy_alpha": {"values": [0.2, 0.4]},
        # "conservative_strategy_min_threshold": {"values": [0.2, 0.3]},

        # solo new strategies on test set
        # "basic_nature": {"values": [17, 21, 22, 23]},
        # "ENV_HPT_mode": {"values": [False]},

        # incorporate new strategies (one each time) on test set
        # "basic_nature": {"values": [17, 18, 19, 20]},
        # "ENV_HPT_mode": {"values": [False]},

        # # oracle strategy set to 0 - solo new strategies on test set
        # "simulation_user_improve": {"values": [0]},
        # "basic_nature": {"values": [17, 21, 22, 23]},
        # "ENV_HPT_mode": {"values": [False]},

        # oracle strategy set to 0 - incorporate new strategies (one each time) on test set
        # "simulation_user_improve": {"values": [0]},
        # "basic_nature": {"values": [18, 19, 20]},
        # "ENV_HPT_mode": {"values": [False]},

    },
    "command": command
}

# Initialize a new sweep
sweep_id = wandb.sweep(sweep=sweep_config, project=project)
print("run this line to run your agent in a screen:")
print(f"screen -dmS \"sweep_agent\" wandb agent {YOUR_WANDB_USERNAME}/{project}/{sweep_id}")

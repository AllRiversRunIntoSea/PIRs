import optuna
import utils.file_tool as file_tool
import math
import utils.general_tool as general_tool
import torch
import framework as fr
import utils.log_tool as log_tool
import logging


class Hyperor:
    def __init__(self, args):
        super().__init__()
        self.args = args
        # self.start_up_trials = 5
        self.study_path = file_tool.connect_path("result", self.args.framework_name, 'optuna')
        file_tool.makedir(self.study_path)
        self.study = optuna.create_study(study_name=self.args.framework_name,
                                         storage='sqlite:///' + file_tool.connect_path(self.study_path, 'study_hyper_parameter.db'),
                                         load_if_exists=True,
                                         pruner=optuna.pruners.MedianPruner())
        # n_startup_trials = self.start_up_trials, n_warmup_steps = 10
        logger_filename = file_tool.connect_path(self.study_path, 'log.txt')
        self.logger = log_tool.get_logger('my_optuna', logger_filename, log_format=logging.Formatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        self.batch_size_list = [8, 16, 32]
        self.learn_rate_list = [5e-5, 3e-5, 2e-5, 1e-5, 2e-6]
        self.trial_times = 30

    def objective(self, trial):
        general_tool.setup_seed(1234)
        # if trial.number == 0:
        #     batch_size = 8
        #     epoch = 3
        #     learn_rate = 2e-5
        #     if self.args.framework_name in self.args.framework_with_gcn:
        #         gcn_layer = 2
        # else:
        batch_size = self.batch_size_list[trial.suggest_int('batch_size_index', 0, len(self.batch_size_list)-1)]
        learn_rate = self.learn_rate_list[trial.suggest_int('learn_rate_index', 0, len(self.learn_rate_list)-1)]
        if self.args.framework_name in self.args.framework_with_gcn:
            gcn_layer = trial.suggest_int('gcn_hidden_layer', 2, 6)
        epoch = trial.suggest_int('epoch', 3, 4)

        self.args.learning_rate = learn_rate
        self.args.per_gpu_train_batch_size = batch_size
        self.args.per_gpu_eval_batch_size = batch_size
        self.args.num_train_epochs = epoch

        if self.args.framework_name in self.args.framework_with_gcn:
            self.args.gcn_layer = gcn_layer

        # self.args.start_up_trials = self.start_up_trials
        if trial.number > 0:
            self.log_trial(self.study.best_trial, 'best trial info')

        framework_manager = fr.FrameworkManager(args=self.args, trial=trial)
        result, attr = framework_manager.run()
        trial.set_user_attr('attributes', result)
        torch.cuda.empty_cache()
        self.log_trial(trial, 'current trial info')

        return result

    def log_trial(self, trial, head=None):
        self.logger.info('*'*80)
        if head is not None:
            self.logger.info(str(head))

        self.logger.info('number:{}'.format(trial.number))
        self.logger.info('user_attrs:{}'.format(trial.user_attrs))
        self.logger.info('params:{}'.format(trial.params))
        if hasattr(trial, 'state'):
            self.logger.info('state:{}'.format(trial.state))
        self.logger.info('*'*80+'\n')

    def tune_hyper_parameter(self):
        self.study.optimize(self.objective, n_trials=self.trial_times)
        self.log_trial(self.study.best_trial, 'best trial info')
        self.study.set_user_attr('learn_rate_list', self.learn_rate_list)
        self.study.set_user_attr('batch_size_list', self.batch_size_list)
        file_tool.save_data_pickle(self.study, file_tool.connect_path(self.study_path, 'study_hyper_parameter.pkls'))
        # log_tool.model_result_logger.info(
        #     'Current best value is {} with parameters: {}.'.format(study.best_value, study.best_params))

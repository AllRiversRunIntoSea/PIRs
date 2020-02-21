import corpus
import framework as fr
import argparse
import utils.hyperor as hyperor
import utils.general_tool as general_tool


def create_arg_dict():
    general_tool.setup_seed(1234)
    arg_dict = {
        'batch_size': 4,
        'learn_rate': 8e-6,
        # 'sgd_momentum': 0.4,
        'optimizer': 'adam',
        'k_fold': 4,
        'epoch': 4,
        'gcn_layer': 6,
        'position_encoding': True,
        'dropout': 0.5,
        'regular_flag': True,
        'ues_gpu': 0,
        'repeat_train': True,
        'corpus': corpus.mrpc.get_mrpc_obj,
        'framework_name': "LSSE",

    }
    parser = argparse.ArgumentParser(description='LSSE')
    parser.add_argument('-gpu', dest="ues_gpu", default='0', type=int,
                        help='GPU order, if value is -1, it use cpu. Default value 0')

    args = parser.parse_args()
    args = vars(args)
    arg_dict.update(args)

    return arg_dict


def run_framework():
    arg_dict = create_arg_dict()
    framework_manager = fr.FrameworkManager(arg_dict)
    framework_manager.train_model()
    # framework_manager.train_final_model()
    # framework_manager.test_model()

def run_hyperor():
    arg_dict = create_arg_dict()
    hyr = hyperor.Hyperor(arg_dict)
    hyr.tune_hyper_parameter()


def main():
    run_framework()
    # run_hyperor()


if __name__ == '__main__':
    main()
    pass
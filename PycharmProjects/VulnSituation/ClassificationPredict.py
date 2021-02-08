# Author: 14281055 Liheng Chen CIT BJTU
# File Name:

import matplotlib.pyplot
import pybrain.datasets
import pybrain.tools.shortcuts
import pybrain.utilities
import pybrain.structure
import pybrain.supervised.trainers
import numpy
import Repository


def percent_error(out, true, threshold=30):
    out_array = numpy.array(out).flatten()
    true_array = numpy.array(true).flatten()
    wrong_number = 0
    for index in range(out_array.size):
        if numpy.abs(out_array[index] - true_array[index]) > threshold:
            wrong_number += 1
    return 100. * float(wrong_number) / float(out_array.size)


def get_classification_data_set(input_np_array, target_np_array, **kwargs):
    classification_data_set = pybrain.datasets.ClassificationDataSet(input_np_array.shape[1],
                                                                     target_np_array.shape[1],
                                                                     **kwargs)
    for sample_index in range(input_np_array.shape[0]):
        classification_data_set.appendLinked(input_np_array[sample_index], target_np_array[sample_index])
    return classification_data_set


def classification_predict(train_input_file_path, train_target_file_path,
                           test_input_file_path, test_target_file_path, test_predict_file_path,
                           layer_node_number_list):
    if layer_node_number_list[-1] < 2:
        return
    class_labels = list(range(layer_node_number_list[-1]))
    print('\rReading Data...', end='')
    train_classification_data_set = get_classification_data_set(
        Repository.excel_to_np_array(train_input_file_path),
        Repository.convert_to_one_hot(Repository.excel_to_np_array(train_target_file_path),
                                      layer_node_number_list[-1]),
        nb_classes=layer_node_number_list[-1], class_labels=class_labels
    )
    test_classification_data_set = get_classification_data_set(
        Repository.excel_to_np_array(test_input_file_path),
        Repository.excel_to_np_array(test_target_file_path),
    )
    print('\rCreating Neural Network...', end='')
    network = pybrain.tools.shortcuts.buildNetwork(*layer_node_number_list,
                                                   outclass=pybrain.structure.SoftmaxLayer)
    bp_trainer = pybrain.supervised.trainers.BackpropTrainer(
        network, train_classification_data_set,
        batchlearning=True
    )
    print('\rTraining...', end='')
    training_errors, validation_errors = bp_trainer.trainUntilConvergence(maxEpochs=10000)

    print('\rPrinting Training And Validation Error...', end='')
    matplotlib.pyplot.plot(training_errors, 'b', validation_errors, 'r')
    matplotlib.pyplot.show()

    print('\rTesting...', end='')
    test_predict = bp_trainer.testOnClassData(test_classification_data_set)

    print('\rGetting Testing Percent Error...', end='')
    test_percent_error = percent_error(
        test_predict,
        test_classification_data_set['target']
    )
    print('\rSaving Testing Predict Output...', end='')
    Repository.np_array_to_excel(numpy.atleast_2d(test_predict).T, test_predict_file_path)
    print("\rEpoch:%d Test Error:%5.2f%%" % (bp_trainer.totalepochs, test_percent_error))


if __name__ == '__main__':
    classification_predict(
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Backup2\train_input.xlsx',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Backup2\train_target.xlsx',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Backup2\test_input.xlsx',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Backup2\test_target.xlsx',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Backup2\test_predict_125_25_300.xlsx',
        [125, 25, 300]
    )

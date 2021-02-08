# Author: 14281055 Liheng Chen CIT BJTU
# File Name: BPNNByEpoch.py

import numpy
import os
import Repository


class BPNeuralNetwork(object):
    def sigmoid(self, x, derivation=False):
        if derivation:
            return self.sigmoid(x) * (1 - self.sigmoid(x))
        else:
            return 1 / (1 + numpy.exp(-x))

    input_data = None
    target_data = None

    layer_input_list = None
    layer_output_list = None

    layer_bias = None

    layer_number = None
    layer_node_number_list = None

    weight_list = []
    correction_matrix_list = []

    layer_output_delta_list = None
    layer_error_list = None

    activation_func = sigmoid

    epochs = 100000000
    goal = 0.00001
    learn_rate = 0.08  # usually in (0,0.1); annealing
    correct_rate = 0.008  # annealing

    loss = None

    weight_file_path = None

    def __init__(self, layer_node_number_list, input_data, target_data=None, weight_file_path=None):
        self.layer_node_number_list = layer_node_number_list

        self.input_data = input_data
        self.target_data = target_data

        self.weight_file_path = weight_file_path

        self.layer_number = len(self.layer_node_number_list)

        self.layer_bias = [0] * (self.layer_number - 1)

        self.layer_input_list = [numpy.array(None)] * self.layer_number
        self.layer_output_list = [numpy.array(None)] * self.layer_number

        self.layer_output_delta_list = [numpy.array(None)] * self.layer_number
        self.layer_error_list = [numpy.array(None)] * self.layer_number

        for layer_index in range(self.layer_number - 1):
            self.weight_list.append(numpy.random.randn(
                layer_node_number_list[layer_index],
                layer_node_number_list[layer_index + 1]
            ) / numpy.sqrt(self.layer_node_number_list[layer_index]))
            self.correction_matrix_list.append(numpy.zeros(self.weight_list[layer_index].shape))
        if self.weight_file_path is not None and os.path.exists(self.weight_file_path):
            self.weight_list = numpy.load(self.weight_file_path)

    def train(self):
        for epoch in range(self.epochs):
            self.loss = 0
            for index in range(self.input_data.shape[0]):
                self.forward_propagation(
                    numpy.atleast_2d(self.input_data[index])
                )
                self.back_propagation(numpy.atleast_2d(self.target_data[index]))
                self.loss += numpy.square(
                    numpy.atleast_2d(self.target_data[index]) - self.layer_output_list[-1]).sum() / 2
            if self.weight_file_path is not None and epoch % 100 == 0:
                numpy.save(os.path.splitext(self.weight_file_path)[0], self.weight_list)
            self.annealing(epoch)
            print('\rEpoch:%d Loss:%f' % (epoch, self.loss), end='')
            if self.loss < self.goal:
                break

    def test(self):
        self.forward_propagation(self.input_data)
        return self.layer_output_list[-1]

    def forward_propagation(self, input_data):
        self.layer_input_list[0] = input_data
        self.layer_output_list[0] = input_data
        for layer_index in range(1, self.layer_number):
            self.layer_input_list[layer_index] = \
                self.layer_output_list[layer_index - 1].dot(self.weight_list[layer_index - 1]) + \
                self.layer_bias[layer_index - 1]
            self.layer_output_list[layer_index] = self.activation_func(self.layer_input_list[layer_index])

    def back_propagation(self, target_data):
        self.layer_output_delta_list[-1] = target_data - self.layer_output_list[-1]
        self.layer_error_list[-1] = \
            self.layer_output_delta_list[-1] * \
            self.activation_func(
                self.layer_input_list[-1],
                derivation=True
            )
        self.weight_list[-1] += self.learn_rate * self.layer_output_list[-2].T.dot(
            self.layer_error_list[-1]) + self.correct_rate * self.correction_matrix_list[-1]
        self.correction_matrix_list[-1] = self.layer_output_list[-2].T.dot(self.layer_error_list[-1])
        for layer_index in range(-2, -self.layer_number, -1):
            self.layer_output_delta_list[layer_index] = \
                self.layer_error_list[layer_index + 1].dot(self.weight_list[layer_index + 1].T)
            self.layer_error_list[layer_index] = \
                self.layer_output_delta_list[layer_index] * \
                self.activation_func(
                    self.layer_input_list[layer_index],
                    derivation=True
                )
            self.weight_list[layer_index] += \
                self.learn_rate * self.layer_output_list[layer_index - 1].T \
                    .dot(self.layer_error_list[layer_index]) \
                + self.correct_rate * self.correction_matrix_list[layer_index]
            self.correction_matrix_list[layer_index] = self.layer_output_list[layer_index - 1].T \
                .dot(self.layer_error_list[layer_index])

    def annealing(self, epoch, step=100000):
        if epoch % step == 0:
            self.learn_rate /= 2  # learn rate annealing
            self.correct_rate /= 2


def train(layer_node_number_list, train_input_file_path, train_target_file_path, weight_file_path=None,
          target_one_hot_flag=False):
    if target_one_hot_flag:
        train_target_one_hot_file_path = Repository.add_suffix_to_file_name(train_target_file_path,
                                                                            '_one_hot')
        if not os.path.exists(train_target_one_hot_file_path):
            Repository.save_one_hot(
                train_target_file_path,
                layer_node_number_list[-1],
                train_target_one_hot_file_path
            )
        train_target_file_path = train_target_one_hot_file_path
    bp_neural_network = BPNeuralNetwork(
        layer_node_number_list,
        Repository.excel_to_np_array(train_input_file_path),
        Repository.excel_to_np_array(train_target_file_path),
        weight_file_path
    )
    bp_neural_network.train()


def test(layer_node_number_list, test_input_file_path, test_predict_file_path, weight_file_path,
         target_one_hot_flag=False):
    bp_neural_network = BPNeuralNetwork(
        layer_node_number_list,
        Repository.excel_to_np_array(test_input_file_path),
        weight_file_path=weight_file_path
    )
    if target_one_hot_flag:
        test_predict_one_hot_file_path = Repository.add_suffix_to_file_name(test_predict_file_path,
                                                                            '_one_hot')
        Repository.np_array_to_excel(bp_neural_network.test(), test_predict_one_hot_file_path)
        Repository.save_one_hot_like_reversal(test_predict_one_hot_file_path, test_predict_file_path)
    else:
        Repository.np_array_to_excel(bp_neural_network.test(), test_predict_file_path)


if __name__ == '__main__':
    train(
        [125, 25, 300],
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Data\train_input_normal_l.xlsx',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Data\train_target.xlsx',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Backup3(My)\weight125_25_300.npy',
        target_one_hot_flag=True
    )
    test(
        [125, 25, 300],
        # r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Data\test_input_normal_l.xlsx',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Data\predict_input_normal.xlsx',
        # r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Backup3(My)\test_predict.xlsx',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Backup3(My)\predict_output.xlsx',
        r'C:\Users\陈力恒\Downloads\VulnerabilitySituation\Backup\Backup3(My)\weight125_25_300.npy',
        target_one_hot_flag=True
    )

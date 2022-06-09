import logging

import fedml
from data.data_loader import load
from fedml.simulation import SimulatorMPI
from model import MobileNetV2, DeepLabV3_plus, VisionTransformer, UNet
from trainer.segmentation_trainer import SegmentationTrainer


def create_model(args, model_name, output_dim):
    logging.info("create_model. model_name = %s, output_dim = %s" % (model_name, output_dim))
    if model_name.lower() == "unet":
        model = UNet()
    elif model_name.lower() == "mobilenetv2":
        model = MobileNetV2()
    elif model_name.lower() == "deeplabv3_plus":
        model = DeepLabV3_plus()
    elif model_name.lower() in ["vit", "transunet"]:
        model = VisionTransformer()
    else:
        raise Exception("such model does not exist !")

    trainer = SegmentationTrainer(model=model)
    logging.info("done")

    return model, trainer


if __name__ == "__main__":
    # init FedML framework
    args = fedml.init()

    # init device
    device = fedml.device.get_device(args)

    # load data
    dataset, class_num = load(args)

    # create model.
    # Note if the model is DNN (e.g., ResNet), the training will be very slow.
    # In this case, please use our FedML distributed version (./fedml_experiments/distributed_fedavg)
    model, trainer = create_model(args, args.model, output_dim=class_num)

    # start training
    try:
        simulator = SimulatorMPI(args, device, dataset, model, trainer)
        simulator.run()
    except Exception as e:
        raise e

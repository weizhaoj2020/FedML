import logging

from .frames.NbAFL import NbAFL_DP
from ..common.ml_engine_backend import MLEngineBackend
from fedml.core.dp.common.constants import DP_LDP, DP_CDP, NBAFL_DP
from fedml.core.dp.frames.cdp import GlobalDP
from fedml.core.dp.frames.ldp import LocalDP
from fedml.core.dp.budget_accountant.dp_accountant import LDPAccountant, CDPAccountant


class FedMLDifferentialPrivacy:
    _dp_instance = None

    @staticmethod
    def get_instance():
        if FedMLDifferentialPrivacy._dp_instance is None:
            FedMLDifferentialPrivacy._dp_instance = FedMLDifferentialPrivacy()
        return FedMLDifferentialPrivacy._dp_instance

    def __init__(self):
        self.dp_solution_type = None
        self.dp_solution = None
        self.dp_accountant = None
        self.is_enabled = False
        self.privacy_engine = None
        self.current_round = 0

    def init(self, args):
        import pdb
        if hasattr(args, "enable_dp") and args.enable_dp:
            logging.info(
                ".......init dp......."
                + args.dp_solution_type
                + "-"
                + args.dp_solution_type
            )
            self.is_enabled = True
            # if hasattr(args, "accountant_type") and args.accountant_type in ["adding"]:
            #     self.enable_accountant = True
            self.dp_solution_type = args.dp_solution_type.strip()
            logging.info("self.dp_solution = {}".format(self.dp_solution_type))

            print(f"dp_solution_type={self.dp_solution_type}")

            if self.dp_solution_type == DP_LDP:
                self.dp_solution = LocalDP(args)
                self.dp_accountant = LDPAccountant(args)
                # total_epsilon = self.dp_accountant.compute_total_epsilon(args)
                # logging.info('LDP total epsilon={}'.format(total_epsilon))
            elif self.dp_solution_type == DP_CDP:
                self.dp_solution = GlobalDP(args)
                self.dp_accountant = CDPAccountant(args)
                # total_epsilon = self.dp_accountant.compute_total_epsilon(args)
                # logging.info('CDP total epsilon={}'.format(total_epsilon))
            elif self.dp_solution_type == NBAFL_DP:
                self.dp_solution = NbAFL_DP(args)
            else:
                raise Exception("dp solution is not defined")

            return args

        if hasattr(args, MLEngineBackend.ml_engine_args_flag) and args.ml_engine in [
            MLEngineBackend.ml_engine_backend_tf,
            MLEngineBackend.ml_engine_backend_jax,
            MLEngineBackend.ml_engine_backend_mxnet,
        ]:
            logging.info(
                "FedMLDifferentialPrivacy is not supported for the machine learning engine: %s. "
                "We will support more engines in the future iteration." % args.ml_engine
            )
            self.is_enabled = False

    def is_dp_enabled(self):
        return self.is_enabled

    def is_local_dp_enabled(self):
        return self.is_enabled and self.dp_solution_type in [DP_LDP]

    def is_global_dp_enabled(self):
        return self.is_enabled and self.dp_solution_type in [DP_CDP]

    def add_local_noise(self, local_grad: dict):
        if self.dp_solution is None:
            raise Exception("dp solution is not initialized!")
        return self.dp_solution.add_local_noise(local_grad)

    def add_global_noise(self, w_locals: dict, qw):
        if self.dp_solution is None:
            raise Exception("dp solution is not initialized!")
        return self.dp_solution.add_global_noise(w_locals, qw)

    def clip_local_update(self, update, clipping_norm):
        return self.dp_solution.clip_local_update(update, clipping_norm)

    def compute_current_epsilon(self, cur_round):
        return self.dp_accountant.compute_current_epsilon(cur_round)

import torch.optim as optim
from torch.utils.data import DataLoader

import time

from autodsac import AutoDSAC
from dataset import SparseDataset
from loss import QuaternionLoss
from models import create_score_nn
from options import parse_args


CAM_IDXS = [3, 1]


if __name__ == '__main__':
    # Parse command line args.
    opt, sid = parse_args()

    # Keep track of training progress.
    train_log = open('log_' + sid + '.txt', 'w', 1)

    # Create dataset, loss, model and AutoDSAC objects.
    train_set = SparseDataset(opt.rootdir, CAM_IDXS, opt.num_frames, opt.num_iterations)
    loss = QuaternionLoss()
    score_nn = create_score_nn(input_size=opt.num_frames*opt.num_joints)
    auto_dsac = AutoDSAC(opt.hypotheses, opt.sample_size, opt.inlier_threshold, 
        opt.inlier_beta, opt.inlier_alpha, loss)

    # Set ScoreNN for optimization (training).
    score_nn.train()
    opt_score_nn = optim.Adam(score_nn.parameters(), lr=opt.learning_rate)
    lrs_score_nn = optim.lr_scheduler.StepLR(opt_score_nn, opt.lr_step, gamma=0.5)

    # Create torch data loader.
    dataloader = DataLoader(train_set, shuffle=False,
                            num_workers=4, batch_size=1)

    # Train loop.
    for iteration, (point_corresponds, gt_3d, gt_Ks, gt_Rs, gt_ts) in enumerate(dataloader):
        start_time = time.time()

        # Call AutoDSAC to obtain camera params and the expected ScoreNN loss.
        camera_params, avg_exp_loss, best_loss = auto_dsac(
            point_corresponds, gt_Ks, gt_3d)

        avg_exp_loss.backward()		# calculate gradients (pytorch autograd)
        score_nn.step()			    # update parameters
        score_nn.zero_grad()	    # reset gradient buffer

        end_time = time.time() - start_time

        print(f'Iteration: {iteration:.6d}, Expected Loss: {avg_exp_loss:2.2f}, '
            f'Bop Loss: {best_loss:2.2f}, Time: {end_time:.2f}s', flush=True)
        train_log.write('%d %f %f %f\n' % (iteration, avg_exp_loss, best_loss))

    train_log.close()

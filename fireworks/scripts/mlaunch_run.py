from argparse import ArgumentParser
import os

from fireworks.core.fw_config import FWConfig
from fireworks.core.fworker import FWorker
from fireworks.core.launchpad import LaunchPad
from fireworks.features.multi_launcher import launch_multiprocess


"""
A runnable script to launch Job Packing Rockets
"""
__author__ = 'Xiaohui Qu'
__copyright__ = 'Copyright 2013, The Electrolyte Genome Project'
__version__ = '0.1'
__maintainer__ = 'Xiaohui Qu'
__email__ = 'xqu@lbl.gov'
__date__ = 'Aug 19, 2013'



def mlaunch():
    m_description = 'This program launches Job Packing Rockets. A Rocket grabs a job from the central database and ' \
                    'runs it.'

    parser = ArgumentParser(description=m_description)

    parser.add_argument('num_rockets', help='the number of jobs to run in parallel', type=int)
    parser.add_argument('--nlaunches', help='number of FireWorks to run per parallel job (int or "infinite"; default 0 is all jobs in DB)', default=0)
    parser.add_argument('--sleep', help='sleep time between loops (secs)', default=None, type=int)

    parser.add_argument('-l', '--launchpad_file', help='path to launchpad file', default=FWConfig().LAUNCHPAD_LOC)
    parser.add_argument('-w', '--fworker_file', help='path to fworker file', default=FWConfig().FWORKER_LOC)
    FWConfig().CONFIG_FILE_DIR = None
    parser.add_argument('-c', '--config_dir', help='path to a directory containing the config file (used if -l, -w unspecified)',
                        default=FWConfig().CONFIG_FILE_DIR)

    parser.add_argument('--loglvl', help='level to print log messages', default='INFO')
    parser.add_argument('-s', '--silencer', help='shortcut to mute log messages', action='store_true')

    parser.add_argument('--nodefile_env', help='environment variable name containing the node file name (for populating FWData, does not affect execution)', default=None, type=str)
    parser.add_argument('--ppn', help='processors per node (for populating FWData, does not affect execution)', default=1, type=int)

    args = parser.parse_args()

    if not args.launchpad_file and args.config_dir and os.path.exists(os.path.join(args.config_dir, 'my_launchpad.yaml')):
        args.launchpad_file = os.path.join(args.config_dir, 'my_launchpad.yaml')

    if not args.fworker_file and args.config_dir and os.path.exists(os.path.join(args.config_dir, 'my_fworker.yaml')):
        args.fworker_file = os.path.join(args.config_dir, 'my_fworker.yaml')

    args.loglvl = 'CRITICAL' if args.silencer else args.loglvl

    launchpad = LaunchPad.from_file(args.launchpad_file) if args.launchpad_file else LaunchPad(strm_lvl=args.loglvl)

    if args.fworker_file:
        fworker = FWorker.from_file(args.fworker_file)
    else:
        fworker = FWorker()

    total_node_list = None
    if args.nodefile_env:
        nodefile = os.environ[args.nodefile_env]
        with open(nodefile, 'r') as f:
            total_node_list = [line.strip() for line in f.readlines()]

    launch_multiprocess(launchpad, fworker, args.loglvl, args.nlaunches,
                                 args.num_rockets, args.sleep, total_node_list,
                                 args.ppn)


if __name__ == "__main__":
    mlaunch()
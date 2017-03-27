__author__ = "Jeffrey Hyman and Satish Karra"
__version__ = "2.0"
__maintainer__ = "Jeffrey Hyman and Satish Karra"
__email__ = "jhyman@lanl.gov"

import  sys 
import os
from time import time
from dfntools import *
import helper

class DFNWORKS(Frozen):
    """  Class for DFN Generation and meshing
    
    Attributes:
        * _jobname: name of job, also the folder where output files are stored
        * _ncpu: number of CPUs used in the job
        * _dfng_en file: the name of the dfng_en input file
        * _dfnflow file: the name of the dfnflow input file
        * _local prefix: indicates that the name contains only the most local directory
        * _vtk_file: the name of the VTK file
        * _inp_file: the name of the INP file
        * _uge_file: the name of the UGE file
        * _mesh_type: the type of mesh
        * _perm_file: the name of the file containing permeabilities 
        * _aper_file: the name of the file containing apertures 
        * _perm_cell file: the name of the file containing cell permeabilities 
        * _aper_cell_file: the name of the file containing cell apertures
        * _dfnt_rans_version: the version of dfnt_rans to use
        * _freeze: indicates whether the class attributes can be modified
        * _large_network: indicates whether C++ or Python is used for file processing at the bottleneck
        of inp to vtk conversion
    """
    from generator import dfng_en
    from flow import dfnflow
    from transport import dfnt_rans
    # Specific functions
    from helper import * # scale, cleanup_files, cleanup_end, commandline_options
    from gen_input import check_input
    from generator import make_working_directory, create_network
    from gen_output import output_report 
    from flow import lagrit2pflotran, pflotran, parse_pflotran_vtk, inp2vtk_python, parse_pflotran_vtk_python, pflotran_cleanup, write_perms_and_correct_volumes_areas, zone2ex 
    from transport import copy_dfnt_rans_files, run_dfnt_rans
    from meshdfn import mesh_network
    from legal import legal
    from paths import define_paths

    def __init__(self, jobname='', local_jobname='',dfng_en_file='',output_file='',local_dfng_en_file='',ncpu='', dfnflow_file = '', local_dfnflow_file = '', dfnt_rans_file = '', inp_file='full_mesh.inp', uge_file='', vtk_file='', mesh_type='dfn', perm_file='', aper_file='',perm_cell_file='',aper_cell_file='', dfnt_rans_version ='', num_frac = ''):

        self._jobname = jobname
        self._ncpu = ncpu
        self._local_jobname = self._jobname.split('/')[-1]

        self._dfng_en_file = dfng_en_file
        self._local_dfng_en_file = self._dfng_en_file.split('/')[-1]
        
        self._output_file = self._dfng_en_file.split('/')[-1]
        
        self._dfnflow_file = dfnflow_file 
        self._local_dfnflow_file = self._dfnflow_file.split('/')[-1]

        self._dfnt_rans_file = dfnt_rans_file 
        self._local_dfnt_rans_file = self._dfnt_rans_file.split('/')[-1]

        self._vtk_file = vtk_file
        self._inp_file = inp_file
        self._uge_file = uge_file
        self._mesh_type = mesh_type
        self._perm_file = perm_file
        self._aper_file = aper_file
        self._perm_cell_file = perm_cell_file
        self._aper_cell_file = aper_cell_file
        self._dfnt_rans_version= 2.0
        self._freeze
        self._large_network = False
        self.legal()

        options = helper.commandline_options()
        if options.large_network ==  True:
            self._large_network = True

def create_dfn(dfng_en_file="", dfnflow_file="", dfnt_rans_file=""):
    '''
    Parse command line inputs and input files to create and populate dfnworks class
    '''
    
    options = helper.commandline_options()
    print("Command Line Inputs:")
    print options
    print("\n-->Creating DFN class")
    dfn = DFNWORKS(jobname=options.jobname, ncpu=options.ncpu)

    if options.input_file != "":
        with open(options.input_file) as f:
            for line in f:
                line=line.rstrip('\n')
                line=line.split()

                if line[0].find("dfng_en") == 0:
                    dfn._dfng_en_file = line[1]
                    dfn._local_dfng_en_file = line[1].split('/')[-1]

                elif line[0].find("dfnflow") == 0:
                    dfn._dfnflow_file = line[1]
                    dfn._local_dfnflow_file = line[1].split('/')[-1]

                elif line[0].find("dfnt_rans") == 0:
                    dfn._dfnt_rans_file = line[1]
                    dfn._local_dfnt_rans_file = line[1].split('/')[-1]
    else:   
        if options.dfng_en != "":
            dfn._dfng_en_file = options.dfng_en
        elif dfng_en_file != "":
            dfn._dfng_en_file = dfng_en_file  
        else:
            sys.exit("ERROR: Input File for dfng_en not provided. Exiting")
        
        if options.dfnflow != "":
            dfn._dfnflow_file = options.dfnflow
        elif dfnflow_file != "":
            dfn._dfnflow_file = dfnflow_file  
        else:
            sys.exit("ERROR: Input File for dfnflow not provided. Exiting")
        
        if options.dfnt_rans != "":
            dfn._dfnt_rans_file = options.dfnt_rans
        elif dfnt_rans_file != "":
            dfn._dfnt_rans_file = dfnt_rans_file  
        else:
            sys.exit("ERROR: Input File for dfnt_rans not provided. Exiting")

    if options.cell is True:
        dfn._aper_cell_file = 'aper_node.dat'
        dfn._perm_cell_file = 'perm_node.dat'
    else:
        dfn._aper_file = 'aperture.dat'
        dfn._perm_file = 'perm.dat'


    print("\n-->Creating DFN class: Complete")
    print 'Jobname: ', dfn._jobname
    print 'Number of cpus requested: ', dfn._ncpu 
    print '--> dfng_en input file: ',dfn._dfng_en_file
    print '--> dfnflow input file: ',dfn._dfnflow_file
    print '--> dfnt_rans input file: ',dfn._dfnt_rans_file
    if options.cell is True:
        print '--> Expecting Cell Based Aperture and Permeability'
    print("="*80+"\n")  

    return dfn


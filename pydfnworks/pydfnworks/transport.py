import os
import sys
import shutil
import helper
from time import time

def dfnt_rans(self):
    '''dfnt_rans
    Copy input files for dfnt_rans into working directory and run DFNTrans
    '''
    print('='*80)
    print("\ndfnt_rans Starting\n")
    print('='*80)

    self.copy_dfnt_rans_files()
    tic=time()
    self.run_dfnt_rans()
    self.cleanup_files('dfnt_rans')
    #helper.dump_time(self._jobname, 'Process: dfnt_rans', time() - tic)   


def copy_dfnt_rans_files(self):
    '''create link to DFNTRANS and copy input file into local directory
    '''
    #Create Path to DFNTrans   
    try:
        os.symlink(os.environ['DFNTRANS_PATH']+'DFNTrans', './DFNTrans')
    except OSError:
        os.remove('DFNTrans')   
        os.symlink(os.environ['DFNTRANS_PATH']+'DFNTrans', './DFNTrans')
    except:
        sys.exit("Cannot create link to DFNTrans. Exiting Program")
    
    # Copy DFNTrans input file
    print(os.getcwd())

    print("Attempting to Copy %s\n"%self._dfnt_rans_file) 
    try:
        shutil.copy(self._dfnt_rans_file, os.path.abspath(os.getcwd())) 
    except OSError:
        print("--> Problem copying %s file"%self._local_dfnt_rans_file)
        print("--> Trying to delete and recopy") 
        os.remove(self._local_dfnt_rans_file)
        shutil.copy(self._dfnt_rans_file, os.path.abspath(os.getcwd())) 
    except:
        print("--> ERROR: Problem copying %s file"%self._dfnt_rans_file)
        sys.exit("Unable to replace. Exiting Program")

def run_dfnt_rans(self):
    '''run dfnt_rans simulation'''
    failure = os.system('./DFNTrans '+self._local_dfnt_rans_file)
    if failure == 0:
        print('='*80)
        print("\ndfnt_rans Complete\n")
        print('='*80)
    else:
        sys.exit("--> ERROR: dfnt_rans did not complete\n")

def create_dfnt_rans_links():
    os.symlink('../params.txt', 'params.txt')
    os.symlink('../allboundaries.zone', 'allboundaries.zone')
    os.symlink('../tri_fracture.stor', 'tri_fracture.stor')
    os.symlink('../poly_info.dat','poly_info.dat')



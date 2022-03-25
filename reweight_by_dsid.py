#!/usr/bin/python
# script to normalize the event weights for mc16e

from ROOT import *
import argparse
from array import array
import os ,sys
r_tag = ["MC16a","MC16d","MC16e"]

dsid = ["364700", "364701", "364702", "364703", "364704",
"364705", "364706", "364707", "364708", "364709", 
"364710", "364711", "364712"]


def parse_options():
        import argparse

        parser = argparse.ArgumentParser(description='Reweight of multiple ntuples')
        parser.add_argument('-d','--directory', help="The directory of ntuples to be reweighted")
        parser.add_argument('-o','--output', help="The output directory")
        parser.add_argument('-t','--tree', default='IsolatedJet_tree', help="The ttree name")
        parser.add_argument('-H','--hist', default='MetaData_EventCount', help="Histogram containing cutflow")
        parser.add_argument('-w','--weight', default='sumw', help="Normalise by 'nevts' or 'sumw'")
        parser.add_argument('-n','--nevents', default=-1, type=int, help="The number of events to loop over (for all -1)")
        opts = parser.parse_args()
        return opts

def main():
        # Read the command-line options
        opts =  parse_options()        
        onlyfiles = [f for f in os.listdir(opts.directory) if os.path.isfile(os.path.join(opts.directory, f))]
        print(onlyfiles)

        hadd_entries = [0,0]
        part_entries = []
        summed = [0,0]
        
        for ttree_name in onlyfiles:
            fin = TFile.Open(opts.directory+'/'+ttree_name,"read")    
            
            t = fin.Get(opts.tree)
            h = fin.Get(opts.hist)

            sumw = -1

            if opts.weight=="nevts":
                sumw = h.GetBinContent(1)
            if opts.weight=="sumw":
                sumw = h.GetBinContent(3)
            if ttree_name == 'a.root':
                hadd_entries[0] = t.GetEntries()
                hadd_entries[1] = sumw
            else:
                part_entries.append([])
                part_entries[-1].append(t.GetEntries())
                part_entries[-1].append(sumw)
            fin.Close()
        if os.path.exists(opts.output):
            os.system("rm -rf "+opts.output)
        os.system("mkdir "+opts.output)
        
        second = lambda x: x[1]
        y = lambda : second (part_entries[0]) 
        print(y)
        #print(part_entries)
        if opts.weight=="sumw":
            part_entries = [part_entries[i][1] for i in range(len(part_entries))]
        if opts.weight=="nevts":
            part_entries = [part_entries[i][0] for i in range(len(part_entries))]
        

        #print(part_entries)

        DSID_TOTAL_WEIGHT = sum(part_entries)
        #print("Total weight for DSID: ",DSID_TOTAL_WEIGHT)
        
        
        
        for ttree_name in onlyfiles:

            
            fin = TFile.Open(opts.directory+"/"+ttree_name,"read")
            t = fin.Get(opts.tree)
            #t.Print()
            print("Total entries: "+str(t.GetEntries()))
            t.SetBranchStatus("*",1)
            t.SetBranchStatus("jet_ConstitE",0)
            h = fin.Get(opts.hist)

            sumw = DSID_TOTAL_WEIGHT
               
            
            

            path_to_output = opts.output 
            print(path_to_output)
            if(opts.nevents == -1):
                opts.nevents = t.GetEntries()
            print("Looping over: ",opts.nevents,"/",t.GetEntries()," events in tree")
            print("Sum of weights=",sumw)
            if sumw==0:
                print("ERROR: sumw==0")

            # Write ttree to new output file
            if (opts.output[-1] == "/"):
                opts.output = opts.output[:-1]
            print(opts.output+"/"+"__reweighted__"+ttree_name)
            
            #print("Creating output file : ",opts.output)
            #fout = TFile(opts.output,"RECREATE")


            fin.Close()

            '''



        '''
        
        tw = t.CloneTree(0)
        #tw.Print()
        tw.SetBranchStatus("*",1)
        w = array('d',[-1])
        b = tw.Branch("weight_tot",w,"weight_tot/D")
        #b.SetEntries(t.GetEntries())
        scale = array('d',[-1])
        b_scale = tw.Branch("sumw",scale,"sumw/D")
        # Loop over events
        for ievt in range(t.GetEntries()):
            #w[0]=-1
            t.GetEntry(ievt)
            if( ievt%100000 == 0 ): 
                print(ievt)
                print(int((ievt/t.GetEntries())*100 ),"%",sep="")
#            print ievt,t.weight

            # Access weight branch, modify it by dividing by sum of weights
            w[0] = t.weight/sumw
           # Sam Meehan : Attention, this is a hack to allow workflow development
           # this branch should be "weight", not only the weight_pileup, but we dont know
           # how to properly configure the IsolatedJetTree code to save that branch to the output
           # w[0] = t.weight_pileup/sumw
            scale[0] = sumw
            #print("sumw: %f, weight: %f, weight_tot: %f"%(sumw,t.weight,w[0]))
            #b.Fill()
            tw.Fill()
            #b_scale.Fill()

            # Stop looping if analysing subset of events
            if ievt > opts.nevents:
                break

        tw.Write()
        
        fout.Close()
        fin.Close()
        print("OUTPUT "+path_to_output+ " is created")
        
        '''

if __name__ == '__main__':
    main()


#  python3 reweight_by_dsid.py  -d /eos/user/d/dtimoshy/IsolatedJets_Out/19022022/user.dtimoshy.364701.MC16a_364701_190222_tree.root -o /eos/user/d/dtimoshy/IsolatedJets_Out/19022022/__reweighted__MC16a_364701_190222_tree.root/
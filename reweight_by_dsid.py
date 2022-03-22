#!/usr/bin/python
# script to normalize the event weights for mc16e

from ROOT import *
import argparse
from array import array
r_tag = ["MC16a","MC16d","MC16e"]

dsid = ["364700", "364701", "364702", "364703", "364704",
"364705", "364706", "364707", "364708", "364709", 
"364710", "364711", "364712"]


def parse_options():
        import argparse

        parser = argparse.ArgumentParser(description='EventLooper')
        parser.add_argument('-i','--input', help="The input file")
        parser.add_argument('-o','--output', help="The output file")
        parser.add_argument('-t','--tree', default='IsolatedJet_tree', help="The ttree name")
        parser.add_argument('-H','--hist', default='MetaData_EventCount', help="Histogram containing cutflow")
        parser.add_argument('-w','--weight', default='sumw', help="Normalise by 'nevts' or 'sumw'")
        parser.add_argument('-n','--nevents', default=-1, type=int, help="The number of events to loop over (for all -1)")
        opts = parser.parse_args()
        return opts

def main():
        # Read the command-line options
        opts =  parse_options()
        
        # Open input file and get ntuple
        fin = TFile.Open(opts.input,"read")
        t = fin.Get(opts.tree)
        #t.Print()
        print("Total entries: "+str(t.GetEntries()))
        t.SetBranchStatus("*",1)
        t.SetBranchStatus("jet_ConstitE",0)
        h = fin.Get(opts.hist)

        sumw = -1
        if opts.weight=="nevts":
            print("use nevts")
            sumw = h.GetBinContent(1)
        if opts.weight=="sumw":
            print("use sumw")
            sumw = h.GetBinContent(3)
        if opts.nevents==-1:
            opts.nevents = t.GetEntries()
        


        path_to_output = opts.output 
        print(path_to_output)
        
        print("Looping over",opts.nevents,"/",t.GetEntries(),"events in tree")
        print("Sum of weights=",sumw)
        if sumw==0:
           print("ERROR: sumw==0")

        # Write ttree to new output file
        print("Creating output file : ",opts.output)
        fout = TFile(opts.output,"RECREATE")
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
        #for ievt in range(0,100):
        #    tw.GetEntry(ievt)
        #    print(ievt)
        #    print("sumw: %f, weight: %f, weight_tot: %f"%(tw.sumw,tw.weight,tw.weight_tot))                                                    
        fout.Close()
        fin.Close()
        print("OUTPUT "+path_to_output+ " is created")
        '''
        '''

if __name__ == '__main__':
    main()

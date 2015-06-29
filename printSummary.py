#!/usr/bin/python

import argparse, subprocess, sys, os.path, re
import utils
sys.path.append('pythonutils')
import compareRootHists
from ROOT import TGraph, TCanvas, TH1F, TLegend, gPad


def setBinLabels(gr,pars):
    h = gr.GetHistogram()
    print h.GetNbinsX(), ' vs ', gr.GetN()
    i = 0
    for p in pars:
        b = h.FindBin(i)
        h.GetXaxis().SetBinLabel(b, p.name + '(' + str(p.i) + ')')
        i = i + 1
    

def plotCmp(filenames):
    fname = filenames[0]
    for fnameloop in filenames:
        if fnameloop==fname:
            continue
        compareRootHists.main(fname,fnameloop,None,'truth',None,True)


def plotResCmp(filenames):
    # assume 36 parameters possible
    c_sum = TCanvas('c_sum','c_sum',10,10,1000,800)
    c_sumNZ = TCanvas('c_sumNonZero','c_sumNonZero',10,10,1000,800)
    c_sum.SetBottomMargin(0.45)
    c_sumNZ.SetBottomMargin(0.45)
    vals = {}
    valsNZ = {}
    icolor = 1
    leg = TLegend(0.78,0.6,0.9,0.87)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetFillColor(0)
    savename = ''
    for filename in filenames:
        if re.match(args.reject,filename) != None:
            print 'skip file ', filename, ' base on pattern ', args.reject
            continue
        if savename=='':
            savename = os.path.splitext(os.path.basename(filename))[0]
        run = utils.getRunNr(filename)
        print run
        savename += '-' + str(run)
        pars = utils.getResResults(filename,False)
        parsNZ = utils.getResResults(filename,True)
        print 'Got ', len(pars), ' for ', filename, 
        print 'Got ', len(parsNZ), ' nonzero for ', filename
        h_sum = TGraph()
        h_sumNZ = TGraph()
        i = 0
        for p in pars:
            #print binmap[p.name], ' ', p.val
            h_sum.SetPoint(i,i,p.val)
            i = i + 1
        i = 0
        for p in parsNZ:
            h_sumNZ.SetPoint(i,i,p.val)
            i = i + 1
        h_sum.SetMarkerStyle(20)
        h_sum.SetMarkerSize(1.0)
        h_sum.SetLineColor(icolor)
        h_sum.SetMarkerColor(icolor)
        h_sumNZ.SetMarkerStyle(20)
        h_sumNZ.SetMarkerSize(1.0)
        h_sumNZ.SetLineColor(icolor)
        h_sumNZ.SetMarkerColor(icolor)
        if len(vals)==0:
            c_sum.cd()
            h_sum.Draw('APL')
            c_sumNZ.cd()
            h_sumNZ.Draw('APL')
            h_sum.SetTitle('Millepede corrections per sensor;;local translation/rotations (mm/rad)')
            h_sumNZ.SetTitle('Millepede corrections per sensor;;local translation/rotation (mm/rad)')
            setBinLabels(h_sum,pars)
            setBinLabels(h_sumNZ,parsNZ)
        else:
            c_sum.cd()
            h_sum.Draw('PL,same')
            c_sumNZ.cd()
            h_sumNZ.Draw('PL,same')
        icolor=icolor+1
        leg.AddEntry(h_sum,'%s'%run,'LP')        
        vals[filename] = h_sum
        valsNZ[filename] = h_sumNZ
    c_sum.cd()
    leg.Draw()
    c_sumNZ.cd()
    leg.Draw()
    c_sum.SaveAs('c_sum_' + savename + '.pdf')
    c_sumNZ.SaveAs('c_sumNZ_' + savename + '.pdf')
    ans = raw_input('press anything to continue')
    

def main(args):
    print "just GO"
    for f in args.files:
        if args.reject != None:
            if re.match(args.reject,f) != None:
                print 'skip file ', f, ' base on pattern ', args.reject
                continue
        utils.printResResults(f)
    if not args.noplots:
        plotResCmp(args.files)
    return 0


    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MP summary script')
    parser.add_argument('-f','--files', nargs='+', required=True, help='Res files.')
    parser.add_argument('-n','--noplots', action='store_true', help='Dont plot anyting.')
    parser.add_argument('-r','--reject', help='Pattern to reject input files.')
    args = parser.parse_args()
    print args
    main(args)

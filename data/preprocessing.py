"""
Script to preprocess scenario data


Copyright (C) 2024 Leonhard Hofbauer, Yueh-Chin Lin, licensed under a MIT license


"""

import sys
import os
import logging
import json


import pandas as pd
import zipfile


logger = logging.getLogger(__name__)


path = "../result_data/"

def load_data(path, exclude=None, include=None):
    """Load and aggregate model data from zip files.
    

    Parameters
    ----------
    path : str
        Path for a result file or to the directory where one or more the 
        results zip files are saved. All zip files in the folder will be 
        loaded.
    exclude: list of str
        List of parameter and variable names to be excluded. The 
        default is None.
    include: list str
        List of parameter and variable names to be include or "all". The 
        default is "all".

    Returns
    -------
    Dict

    """
    
    if not os.path.exists(path):
        logger.warning('The result directory or file does not exist.')
        return
    
    logger.info("Loading results")
    
    if os.path.isfile(path):
        packf = [path]
    
    else:
        # add seperator in the end if not present
        path = os.path.join(path, '')
    
        # create list of all zip files in directory
        packf = sorted([path+f for f in os.listdir(path) if f.endswith('.zip')])
        if not packf:
            logger.warning("There are no results in the directory to load.")
            return          
        
    results = []


    # go through each zip file and add as dictionary to results list
    for f in packf:
        run = dict()
        
        zf = zipfile.ZipFile(f)
        pack = json.load(zf.open('datapackage.json'))
        run['name'] = pack["name"]
        
        for r in pack["resources"]:
            if exclude is not None and r["title"] in exclude:
                continue
            if (include == "all") or (include !="all" and r["title"] in include):
                run[r["title"]] = pd.read_csv(zf.open(r["path"]),
                                           index_col=r['schema']['primaryKey'])
                
                #FIXME: delete, arbitrary renaming for test purposes
                run[r["title"]] = run[r["title"]].rename(index={'NODE_UK|LA|SO':'nz-2050_hp-00',
                                                                'NZ_UK|LA|SO':'nz-2045_hp-00',
                                                                'NZDH_UK|LA|SO':'nz-2040_hp-00',
                                                                'NZHP_UK|LA|SO':'nz-2050_hp-01',
                                                                'NZLP_UK|LA|SO':'nz-2045_hp-01',
                                                                'NZHY_UK|LA|SO':'nz-2040_hp-01'})
            
        results.append(run)
    
    logger.info("Loaded results")


    logger.info("Aggregate results")
    
    res = list()
    if len(results) == 1:
        res = res + results
   
    else:
        result = results[0]
        
   
        for k,v in result.items():
            if k == "name":
                result[k] = "aggregation_of_runs"
                continue
            v = pd.concat([v]+[r[k] for r in results[1:] if k in r],
                          axis=0,join="inner")
            result[k] = v.groupby(level=[i for i in
                                  range(v.index.nlevels)]).sum()
        res.append(result)
   
    results = res
    
    return results


def arrange_data(results, var, x, xy=False,xfilter=None, xscale=None,
                 zfilter=None, zgroupby=None,cgroupby=None,
                 filter_in=None, filter_out=None,ffilter=None,fgroupby=None,
                 an_change=False,
                 cleanup=True,
                 relative=None,zorder=None, naming=None, **kwargs):
    """ Arrange data for dashboard.
    

    Parameters
    ----------
    var : str
        Name of the result variable to be used.
    x : str or list
        Name of set(s) to be used as dimension of the x-axis.
    xfilter : list, optional
        List of labels for which x-axis labels are tested and excluded if 
        not present in list. The default is None.
    xscale : series, optional
        Series that provides scaling factors for the data (values) for
        certain x-labels (index). This is mainly relevant if values
        represent multi-year periods that are to be scaled to an average
        year. The default is None.
    zfilter : dict, optional
        Dict to filter the data, i.e.,
        pick values (dict values) for certain sets (dict keys) and
        discard the remaining data. The default is None.
    zgroupby : str, or list of str, optional
        A set or list of sets indicating the levels to which data is
        grouped/aggregated. The default is None.
    cgroupby : dict, or func, optional
        A dict or function mapping level values to an aggregate value.
        The default is None.
    filter_in : dict of lists, optional
        Dict of list (of strings) for which data labels are tested and if 
        NOT present are excluded. Dict keys are the index level names.
        The default is None.
    filter_out : dict of lists, optional
        Dict of list (of strings) for which data labels are tested and if 
        present are excluded. Dict keys are the index level names.
        The default is None.
    zorder : list, optional
        List of z-axis labels that is used to reorder (only relevant for
        appearance in some graph types). The default is None.
    naming : Series, optional
        Pandas Series that map names from the model (index) to names to 
        be used for the graph. The default is None.
    relative : str, optional
        String which gives the level which is used to calculate the
        relative values. If none is given, absolute values are plotted.
        The default is None.
    rel_filter_str_in : tuple, optional
        Tuple to filter the data used to calculate base for calculating
        the relative data, i.e., pick a string (second value) for certain
        sets (first value) and discard the all values that do not contain
        the string. The default is None.
    **kwargs : dict, optional
        Additional arguments passed to the DataFrame plot function.

    Returns
    -------
    df : DataFrame
        DataFrame with the data.

    """
    

    if var not in results[0].keys():
        logger.warning("Attribute '{}' not found.".format(var))
        return
    else:
        df = results[0][var].copy()
   
    
    # convert x to list if given as string
    if isinstance(x,str):
        x = [x]
        
    # choose values for specific z dimensions
    if zfilter is not None:
        df = df.xs([v for v in zfilter.values()],
                   level=[k for k in zfilter.keys()],
                   axis=0)
    logger.info("Plot 3")
    
    # filter
    if (filter_in is not None) or (filter_out is not None):
        lab = dict()
        ind = df.index.to_frame()
        for il in df.index.names:
            
            if ((filter_in is not None) and (filter_out is not None) and
                (il in filter_in.keys()) and (il in filter_out.keys())):
                lab[il] = [e for e in ind[il].unique()
                           if any(str(s) in str(e) for s in filter_in[il]) and
                            all(str(s) not in str(e) for s in filter_out[il])]
            elif ((filter_in is not None) and (il in filter_in.keys())):
                lab[il] = [e for e in ind[il].unique()
                           if any(str(s) in str(e) for s in filter_in[il])]
            elif ((filter_out is not None) and (il in filter_out.keys())):
                lab[il] = [e for e in ind[il].unique()
                           if all(str(s) not in str(e) for s in filter_out[il])]
            else:
                lab[il] = slice(None)
        df = df.loc[tuple([s for s in lab.values()]),:]
        
    logger.info("Plot 4")    
    # scale values if required  
    if xscale is not None:
        df.loc[:,"VALUE"] = df["VALUE"].multiply(xscale,axis=0)#.combine_first(df)
        
 
    
    # groupby given z dimension
    if zgroupby is not None:
        df = df.groupby(level=list(set(zgroupby+x)), axis=0).sum()
    

    # groupby content of level based on function or dict
    if cgroupby is not None:
        for k,v in cgroupby.items():
            idx = df.index.to_frame()
            if isinstance(v, dict):
                agg = df.index.get_level_values(k).to_series().replace(v).to_list()
            if callable(v):
                agg = [v(i) for i in df.index.get_level_values(k)]
            
            idx = idx.rename(columns={k:k+"_"})
            idx.insert(list(idx.columns).index(k+"_"), k, agg)
            df.index = pd.MultiIndex.from_frame(idx)
    
        df = df.groupby([l for l in df.index.names if l[:-1] not in list(cgroupby.keys())], axis=0).sum()
        

    # calculate relative values if required
    if relative is not None:
        if isinstance(relative,list):
            df = df/df.groupby([i for i in df.index.names if i not in relative],
                               axis=0).sum()
        if isinstance(relative,dict):
            df = df/df.xs([v for v in relative.values()],
                       level=[k for k in relative.keys()],
                       axis=0)

    if an_change:
        dfdiv = df.copy()
        dfdiv["YEAR"] = dfdiv.index.get_level_values("YEAR")
        df = df.groupby(level=[i for i in df.index.names
                         if i !="YEAR"]).diff()["VALUE"].div(dfdiv.groupby(level=[i for i in df.index.names
                         if i !="YEAR"]).diff()["YEAR"]).to_frame()
                                                                
    # groupby given z dimension
    if fgroupby is not None:
        for k in fgroupby.keys():
            # df = getattr(df.groupby(level=list(set(fgroupby[k]+[x])),
            #                         axis=0),k)()  
            idx = df.abs().groupby(level=list(set(fgroupby[k])),
                                    axis=0).idxmax()
           
            df = df.loc[idx[0]]
    
    if ffilter is not None:
        df = df.loc[tuple([ffilter[n] if n in ffilter.keys()
                           else slice(None)
                           for n in df.index.names]),:]
        


    if  cleanup:
        # remove any negative numbers (due to inaccuracies when solving)
        df[df<0] = 0
        # remove any columns if all values are zero (tolerance of 10^-14)
        df = df.loc[:,df.max()>10**-20]
    

    # unstack all but x dimensions and drop top level "VALUE" column level
    df = df.unstack([i for i in df.index.names if i not in x])
    df.columns = df.columns.droplevel()
         

    # order z dimension entries
    if zorder is not None:
        df = df[[c for c in zorder if c in df.columns]
                +[c  for c in df.columns if c not in zorder]]


    if xy:
        kwargs["x"] = df.index[0]
        kwargs["y"] = df.index[1]
        df = df.T
        
    # rename if necessary
    if naming is not None:
        df = df.rename(index=naming)
        df = df.rename(columns=naming)

    return df


if __name__ == "__main__":
    
    # load data
    
    data = load_data(path,include=["TotalProductionByTechnologyAnnual",
                                   "CostTotalProcessed",
                                   "AnnualEmissions"])
    
    # config for data processing
    zo = ["NGBO","OIBO","ELST","ELRE","BMBO","HIUM","ASHP","AWHP","GSHP","H2BO",
          "BELO", "BEST"]
    
    naming = pd.read_csv("./data/naming.csv",
                         index_col=["NAME_IN_MODEL"])
    naming = naming["NAME"]
    
    years_map = pd.Series([2015]*6+[2021]*2+[2023]*2+
                          [e for e in list(range(2025,2056,5))
                           for i in range(5)]+
                          [2060]*1,
                          index=range(2015,2061))
    xscale=1/years_map.value_counts()
    xscale.index.name="YEAR"
    xscale.name="VALUE"
    
    
    # Data analysis element 01 –  Heat generation graph 
    #s = "NZ_UK|LA|SO"
    plot_data_01 = arrange_data(results=data,
                             var="TotalProductionByTechnologyAnnual",
                             x = "YEAR",
                             xscale=xscale,
                             filter_in={"YEAR":[2015,2022,2023,2025,2030,
                                                2035,2040,2045,2050,2055],
                                        "TECHNOLOGY":["DD","DNDO"]},
                             filter_out={"TECHNOLOGY":["RAUP","WDIS"]},
                             zgroupby=["RUN","TECHNOLOGY"],
                             cgroupby={"TECHNOLOGY":lambda x: x[0:4]},
                             naming=naming,
                             #zorder=zo,
                             )
    plot_data_01 = plot_data_01.stack(1)
    # save data
    plot_data_01.to_csv("./data/plot_data_01.csv")
    
    # Data analysis element 02 –  Heat generation hex maps
    plot_data_02 = arrange_data(results=data,
                             var="TotalProductionByTechnologyAnnual",
                             x = "YEAR",
                             xscale=xscale,
                             filter_in={"YEAR":[2015,2022,2023,2025,2030,
                                                2035,2040,2045,2050,2055],
                                        "TECHNOLOGY":["DD","DNDO"]},
                             filter_out={"TECHNOLOGY":["RAUP","WDIS"]},
                             zgroupby=["RUN","REGION","TECHNOLOGY"],
                             cgroupby={"TECHNOLOGY":lambda x: x[0:4],
                                       "REGION":lambda x: x[0:9]},
                             relative=["TECHNOLOGY"],
                             naming=naming,
                             #zorder=zo,
                             )
    plot_data_02 = plot_data_02.stack([1,2])
    # save data
    plot_data_02.to_csv("./data/plot_data_02.csv")   
    
    
    # Data analysis element 03 –  Cost structure graph   
    
    def groupby(x):
        if ("WDIS" in x) or ("RAUP" in x):
            n = "Building Heat Dist."
        elif x.startswith("BE"):
            n = "Building Heat Eff."
        elif ("DD" in x) or ("DNDO" in x):
            n = "Building Heat Gen."
        elif x.startswith("DH") or ("SDIS" in x):
            n = "DH systems"
        elif ("TDIS" in x) or ("TTRA") in x:
            n = "T&D (except DH)"
        elif (("SNAT" in x) or ("SEXT" in x)) and ("BS" not in x[2:]):
            n = "Supply"
        else:
            n = "Others"   
        return n

    plot_data_03 = arrange_data(results=data,
                             var="CostTotalProcessed",
                             x = ["YEAR"],
                             xscale=xscale,
                             filter_in={"YEAR":[2015,2022,2023,2025,2030,
                                                2035,2040,2045,2050,2055]},
                             zgroupby=["RUN","TECHNOLOGY"],
                             cgroupby={"TECHNOLOGY":groupby},
                             naming=naming,
                             #zorder=zo,
                             )
    
    plot_data_03 = plot_data_03.stack([0,1]).to_frame()
    plot_data_03.columns = ["VALUE"]
    # save data
    plot_data_03.to_csv("./data/plot_data_03.csv")   
    
    # Data analysis element 04 –  Investment cost graph 
    # This would use the "CostCapitalProcessed" parameter and below shows the
    # filter_in and filter_out that could be used to separate the technologies in
    # the different sectors
    
    # groupbyl = {"TECHNOLOGY":lambda x: x[0:6]}
    # groupbys = {"TECHNOLOGY":groupby}

    
    # plots = [{"gb":groupbyl,
    #           "fin":["TDIS","TTRA"],
    #           "fout":[],
    #           "title" :"Networks"},
    #          {"gb":groupbyl,
    #             "fin":["DH","SDIS"],
    #             "fout":["DHMT"],
    #             "title" : "District heating"},
    #          {"gb":groupbyl,
    #         "fin":["HPSNAT"],
    #         "fout":[],
    #         "title" :"H2 production"},
    #          {"gb":groupbys,
    #             "fin":["DD","DNDO"],
    #             "fout":[],
    #             "title" : "Building techs"}
    #         ]

    # Data analysis element 05 –  Net zero maps
    
    reduction_value = 0.05
    
    em = data[0]["AnnualEmissions"].copy()
    # divide by number of years in period to get average annual emissions
    em["VALUE"] = em["VALUE"].multiply(xscale,axis=0)
    
    # normalize with respect to base year
    plot_data_05 = em /em.xs(2015, level=3)
    # process to get first year emission reduction is achieved
    plot_data_05 = plot_data_05.loc[plot_data_05["VALUE"]<=reduction_value]
    plot_data_05 = plot_data_05.reset_index("YEAR")
    plot_data_05 = plot_data_05.drop("VALUE",axis=1)
    plot_data_05 = plot_data_05.groupby(["RUN","REGION","EMISSION"]).min()
    plot_data_05 = plot_data_05.rename(columns={"YEAR":"VALUE"})
    
    # save data
    plot_data_05.to_csv("./data/plot_data_05.csv")
    
    
    # Data analysis element 07 –  Local heat generation
    
    plot_data_07 = arrange_data(results=data,
                             var="TotalProductionByTechnologyAnnual",
                             x = "YEAR",
                             xscale=xscale,
                             filter_in={"YEAR":[2015,2022,2023,2025,2030,
                                                2035,2040,2045,2050,2055],
                                        "TECHNOLOGY":["DD","DNDO"]},
                             filter_out={"TECHNOLOGY":["RAUP","WDIS"]},
                             zgroupby=["RUN","TECHNOLOGY","REGION"],
                             cgroupby={"TECHNOLOGY":lambda x: x[0:4],
                                       "REGION":lambda x: x[0:9]},
                             naming=naming,
                             #zorder=zo,
                             )
    plot_data_07 = plot_data_07.stack([1,2])
    # save data
    plot_data_07.to_csv("./data/plot_data_07.csv")
    
    # Data analysis element 08 –  Local cost structure graph   
    
    def groupby(x):
        if ("WDIS" in x) or ("RAUP" in x):
            n = "Building Heat Dist."
        elif x.startswith("BE"):
            n = "Building Heat Eff."
        elif ("DD" in x) or ("DNDO" in x):
            n = "Building Heat Gen."
        elif x.startswith("DH") or ("SDIS" in x):
            n = "DH systems"
        elif ("TDIS" in x) or ("TTRA") in x:
            n = "T&D (except DH)"
        elif (("SNAT" in x) or ("SEXT" in x)) and ("BS" not in x[2:]):
            n = "Supply"
        else:
            n = "Others"   
        return n

    plot_data_08 = arrange_data(results=data,
                                var="CostTotalProcessed",
                                x = ["YEAR"],
                                xscale=xscale,
                                filter_in={"YEAR":[2015,2022,2023,2025,2030,
                                                2035,2040,2045,2050,2055]},
                                zgroupby=["RUN","TECHNOLOGY","REGION"],
                                cgroupby={"TECHNOLOGY":groupby,
                                          "REGION":lambda x: x[0:9]},
                                naming=naming,
                                #zorder=zo,
                                )
    
    plot_data_08 = plot_data_08.stack([1,2])
    # save data
    plot_data_08.to_csv("./data/plot_data_08.csv")   
    
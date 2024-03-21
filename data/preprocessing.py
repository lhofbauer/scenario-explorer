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


rpath = "../../result_data/"
dpath = "../data/"

rpath = "../../results/"
dpath = "../data/"

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


def arrange_data(results, var, xy=False,xfilter=None, xscale=None,
                 zfilter=None, zgroupby=None,cgroupby=None,
                 filter_in=None, filter_out=None,ffilter=None,fgroupby=None,
                 an_change=False,
                 cleanup=True,
                 relative=None,zorder=None,reagg=None,
                 naming=None, **kwargs):
    """ Arrange data for dashboard.
    

    Parameters
    ----------
    var : str
        Name of the result variable to be used.
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
    reagg : dict, optional
        Dictionary that is used to rename index labels after groupby
        operations and performs another groupby to aggregate.
        The default is None.        
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
        df = df.groupby(level=list(set(zgroupby))).sum()
    

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
    
        df = df.groupby([l for l in df.index.names if l[:-1] not in list(cgroupby.keys())]).sum()
        

    # calculate relative values if required
    if relative is not None:
        if isinstance(relative,list):
            df = df/df.groupby([i for i in df.index.names if i not in relative]
                               ).sum()
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
            
    if reagg is not None:
        df = df.rename(index=reagg)
        df = df.groupby(df.index.names).sum()
        
    # order z dimension entries
    if zorder is not None:
        techs = df.index.get_level_values("TECHNOLOGY").unique()
        od = ([c for c in zorder if c in techs]
                +[c for c in techs if c not in zorder])
        
        df = df.reindex(level="TECHNOLOGY", labels=od)
    


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
    data = load_data(rpath,include=["TotalProductionByTechnologyAnnual",
                                   "CostTotalProcessed",
                                   "AnnualEmissions",
                                   "CostCapital",
                                   "NewCapacity",
                                   "DemandCost",
                                   "SpecifiedAnnualDemand",
                                   "SpecifiedDemandProfile"])
    
    # config for data processing
    zo = ["NGBO","OIBO","ELST","ELRE","BMBO","HIUM","ASHP","AWHP","GSHP","H2BO",
          "BELO", "BEST","BEFF"]
    
    naming = pd.read_csv(dpath+"naming.csv",
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
    
    tech_agg = {"BEST":"BEFF",
                "BELO": "BEFF",
                "BEME": "BEFF",
                "BEHI": "BEFF",
                "AAHP": "ASHP",
                "AWHP": "ASHP"}
    scenarios = list(data[0]
                     ["NewCapacity"].index.get_level_values("RUN").unique())
    
    mapping = pd.read_csv(dpath+'Local_Authority_District_to_Country_(April_2023)_Lookup_in_the_United_Kingdom.csv',
                      usecols=["LAD23CD","LAD23NM"],
                      index_col=["LAD23CD"])
    mapping.index.name="REGION"
    mapping = mapping ["LAD23NM"]
    # Data analysis element 01 –  Heat generation data
    plot_data_01 = arrange_data(results=data,
                             var="TotalProductionByTechnologyAnnual",
                             xscale=xscale,
                             filter_in={"YEAR":[2015,2022,2023,2025,2030,
                                                2035,2040,2045,2050,2055],
                                        "TECHNOLOGY":["DD","DNDO"]},
                             filter_out={"TECHNOLOGY":["RAUP","WDIS"]},
                             zgroupby=["YEAR","RUN","TECHNOLOGY"],
                             cgroupby={"TECHNOLOGY":lambda x: x[0:4]},
                             reagg=tech_agg,
                             naming=naming,
                             zorder=zo,
                             )
    # save data
    plot_data_01.to_csv(dpath+"plot_data_01.csv")
    
    
    # Data analysis element 02 –  Heat generation local data (maps)
    plot_data_02 = arrange_data(results=data,
                             var="TotalProductionByTechnologyAnnual",
                             xscale=xscale,
                             filter_in={"YEAR":[2015,2022,2023,2025,2030,
                                                2035,2040,2045,2050,2055],
                                        "TECHNOLOGY":["DD","DNDO"]},
                             filter_out={"TECHNOLOGY":["RAUP","WDIS"]},
                             zgroupby=["RUN","REGION","TECHNOLOGY","YEAR"],
                             cgroupby={"TECHNOLOGY":lambda x: x[0:4],
                                       "REGION":lambda x: x[0:9]},
                             reagg=tech_agg,
                             relative=["TECHNOLOGY"],
                             naming=naming,
                             zorder=zo,
                             )

    
    plot_data_02.to_csv(dpath+"plot_data_02.csv")
    
    # save data

    plot_data_02n = plot_data_02.copy().reset_index()
    plot_data_02n["REGION"] = plot_data_02n["REGION"].map(mapping)
    plot_data_02n.to_csv(dpath+"plot_data_02n.csv",index=False)
       
    # Data analysis element 03 –  Cost structure data
    
    def groupby(x):
        if ("WDIS" in x) or ("RAUP" in x):
            n = "Building heat distribution"
        elif x.startswith("BE"):
            n = "Building retrofit"
        elif ("DD" in x) or ("DNDO" in x):
            n = "Building heat technologies"
        elif x.startswith("DH") or ("SDIS" in x):
            n = "District heating systems"
        elif ("TDIS" in x) or ("TTRA" in x):
            n = "Gas and power networks"
        elif (("SNAT" in x) or ("SEXT" in x)) and ("BS" not in x[2:]):
            n = "Energy supply"
        else:
            n = "Others"   
        return n
    
    order = ["Energy supply","Networks","District heat","Building retrofit",
             "Building heating","Wet heating system","Others"]
    plot_data_03 = arrange_data(results=data,
                             var="CostTotalProcessed",
                             xscale=xscale,
                             filter_in={"YEAR":[2015,2022,2023,2025,2030,
                                                2035,2040,2045,2050,2055]},
                             zgroupby=["YEAR","RUN","TECHNOLOGY"],
                             cgroupby={"TECHNOLOGY":groupby},
                             naming=naming,
                             zorder=order,
                             )
    
    # convert to billions
    plot_data_03.loc[:,"VALUE"] =  plot_data_03["VALUE"]/1000
    
    # save data
    plot_data_03.to_csv(dpath+"plot_data_03.csv")   
    
    
    
    # Data analysis element 04 –  Investment cost data 
    def groupby(x):
        if ("ASHP" in x) or ("GSHP" in x) or ("AWHP" in x):
            n = "Heat pumps"
        elif ("WDIS" in x) or ("RAUP" in x):
            n = "Wet heating system"
        elif x.startswith("BE"):
            n = "Building retrofit"
        elif ("OIBO" in x) or ("NGBO" in x):
            n = "Fossil fuel boilers"
        elif ("ELST" in x) or ("ELRE" in x):
            n = "Electric heating"
        elif ("HIUM" in x):
            n = "Heat interface"
        else:
            n = "Others"   
        return n
    
    groupbyl = {"TECHNOLOGY":lambda x: x[0:6],
                "REGION":lambda x: x[0:9]}
    groupbys = {"TECHNOLOGY":groupby,
                "REGION":lambda x: x[0:9]}

    
    plots = [{"gb":groupbyl,
              "fin":["TDIS","TTRA"],
              "fout":[],
              "title" :"Networks",
              "short":"net"},
              {"gb":groupbyl,
                "fin":["DH","SDIS"],
                "fout":["DHMT"],
                "title" : "District heating",
                "short":"dh"},
              {"gb":groupbyl,
            "fin":["HPSNAT"],
            "fout":[],
            "title" :"H2 production",
            "short":"h2"},
              {"gb":groupbys,
                "fin":["DD","DNDO"],
                "fout":[],
                "title" : "Building techs",
                "short":"build"}
            ]

    plot_data_4 = list()
    for d in plots:
        plot_data_4.append(arrange_data(results=data,
                                  var="CostCapital",
                                  #xscale=xscale,
                                  filter_in={"TECHNOLOGY":d["fin"],
                                             "YEAR":[2023,2025,2030,
                                                     2035,2040,2045,2050]},
                                  filter_out={"TECHNOLOGY":d["fout"]},
                                  zgroupby=["RUN","REGION","TECHNOLOGY"],
                                  cgroupby=d["gb"],
                                  naming = naming))
        
    for d,p in zip(plot_data_4,plots):

        # convert to per year
        d["VALUE"] =  d["VALUE"]/(2054-2023)
        d = d.reset_index()
        d.loc[:,"REGION"] = d.loc[:,"REGION"].map(mapping)
        
        # save data
        d.to_csv(dpath+f"plot_data_04_loc_{p['short']}.csv",index=False)  
        
        # convert to billions
        d["VALUE"] =  d["VALUE"]/1000
        g = d.groupby(["RUN","TECHNOLOGY"]).sum()
        g.to_csv(dpath+f"plot_data_04_{p['short']}.csv") 




    # Data analysis element 05 –  Net zero maps
    
    reduction_value = 0.02
    
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
    plot_data_05.to_csv(dpath+"plot_data_05.csv")


    # Data analysis element 10 –  Emission pathways
     
    em = data[0]["AnnualEmissions"].copy()
    # divide by number of years in period to get average annual emissions
    em["VALUE"] = em["VALUE"].multiply(xscale,axis=0)
    
    plot_data_10 = em.xs("UK",level="REGION")
    plot_data_10_loc = em.reset_index()
    plot_data_10_loc.loc[:,"REGION"] = plot_data_10_loc.loc[:,"REGION"].map(mapping)
    
    # save data
    plot_data_10.to_csv(dpath+"plot_data_10.csv")    
    plot_data_10_loc.to_csv(dpath+"plot_data_10_loc.csv",index=False)
    
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

    # save data
    plot_data_07.to_csv(dpath+"plot_data_07.csv")
    
    
    
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
    
    # save data
    plot_data_08.to_csv(dpath+"plot_data_08.csv")   
    
    
    # Data analysis element 09 –  HP installations - domestic ASHP
    
    # to load from model data
    # techcaps = pd.read_csv("PATHTODIR/heat_peak_dwelling.csv",index_col=("LSOA11CD",
    #                                                            "TECHNOLOGY"))
    # # FIXME: this could use the data for each property type and LA not just the
    # # average (not possible when using this calculation elsewhere to set
    # # deployment constraint)
    # techcaps = techcaps.xs("AVERAGE")
    # techcaps = techcaps.drop("PROPERTY_TYPE",axis=1)
    # techcaps = techcaps.groupby("TECHNOLOGY").mean()
    # techcaps = pd.to_csv("./data/dwelling_tech_caps.csv")
    
    
    # to load from processed file
    techcaps = pd.read_csv(dpath+"dwelling_tech_caps.csv",
                           index_col=("TECHNOLOGY"))
    
    tech_agg = {"ASHP":"HP",
                "GSHP": "HP"}
    plot_data = arrange_data(results=data,
                            var="NewCapacity",
                            xscale=xscale,
                            filter_in={"YEAR":[2015,2022,2023,2025,2030,
                                            2035,2040,2045,2050,2055],
                                       "TECHNOLOGY":["ASHPDD","GSHPDD"]},
                            zgroupby=["RUN","REGION","TECHNOLOGY","YEAR"],
                            cgroupby={"TECHNOLOGY":lambda x: x[0:4],
                                      "REGION":lambda x: x[0:9]
                                      },
                            reagg=tech_agg,
                            #naming=naming,
                            #zorder=zo,
                            )
    plot_data_09l = plot_data/techcaps.loc["ASHP"].mean()
    plot_data.groupby(["RUN","TECHNOLOGY","YEAR"]).sum()
    plot_data_09l = plot_data_09l.reset_index()
    plot_data_09l["REGION"] = plot_data_09l["REGION"].map(mapping)
    # FIXME: this is a simplified calc, might need to improve
    plot_data_09 = (plot_data.groupby(["RUN","TECHNOLOGY","YEAR"]).sum()
                    /techcaps.loc["ASHP"].mean())

    #df = df.divide(techcaps["peakcap"],level="TECHNOLOGY")*10**6
    
    # save data
    plot_data_09.to_csv(dpath+"plot_data_09.csv")   
    plot_data_09l.to_csv(dpath+"plot_data_09l.csv",index=False) 
    
    
    
    # Data analysis element 11 –  Local heating cost


    
    # FIXME: delete if GDHI not used
    # load economic data on household income
    #snakemake.input.path_ec_gdhi
    # path = "../raw_data/economic/GDHI/"
    # files = sorted(os.listdir(path))
    # files = [file for file in files if file.endswith(".xlsx")]
    
    # data = list()
    
    # for f in files:
    #     df = pd.read_excel(path+f,sheet_name="Table 3",skiprows=1,index_col=(1))
    #     data.append(df)
    # gdhi = pd.concat(data)
    # gdhi.index.name="REGION"
    # gdhi = gdhi[gdhi["Region"]!="Northern Ireland"]
    # gdhi = gdhi.iloc[:,2:]
    # gdhi = utils.update_LADCD(gdhi,from_CD="LAD21CD",how="mean")
    
    
    # calculate demand
    ecs = ["HWDDDE", "HWDDFL", "HWDDSD", "HWDDTE",
           "SHDDDE", "SHDDFL", "SHDDSD", "SHDDTE"]
    ecs = ["HWDDFL","SHDDFL"]
    dem = (data[0]["SpecifiedAnnualDemand"]
           *data[0]["SpecifiedDemandProfile"]).dropna()
    dem = dem[dem.index.get_level_values("FUEL").str.startswith(tuple(ecs))]
    dem = dem.reset_index().drop(["FUEL","TIMESLICE"],axis=1)
    dem["REGION"] = dem["REGION"].str[:9]
    dem = dem.groupby(["RUN","REGION","YEAR"]).sum()
    
    print(dem)
    # get number of properties
    pnum = pd.read_csv(dpath+'number_properties.csv',index_col=["REGION",
                                                                 "PROPERTY_TYPE",
                                                                 "YEAR"])
    
    ptd = {"TE":"Terraced",
           "FL":"Flats",
           "DE":"Detached",
           "SD":"Semi-detached"}
    pt = {ptd[ec[-2:]] for ec in ecs }
    pnum = pnum[pnum.index.get_level_values("PROPERTY_TYPE").str.startswith(tuple(pt))]
    pnum = pnum.groupby(["REGION","YEAR"]).sum()
    pnum = pd.concat([pnum]*len(scenarios),
                     keys=scenarios, names=['RUN'])


    print(pnum)                                                          
    cost = data[0]["DemandCost"].groupby(["RUN","REGION","FUEL","YEAR"]).sum()
    cost = cost[cost.index.get_level_values("FUEL").str.startswith(tuple(ecs))]
    cost = cost.reset_index().drop(["FUEL"],axis=1)
    cost["REGION"] = cost["REGION"].str[:9]
    cost = cost.groupby(["RUN","REGION","YEAR"]).sum()
    print(cost)
    # calculate cost per demand or property
    data[0]["CostPerDomHeat"] = (cost/dem)
    data[0]["CostPerDomHeat"] = data[0]["CostPerDomHeat"]* 10**6
    
    data[0]["CostPerDomProp"] = (cost/pnum) * 10**6
    agg = (cost.groupby(["RUN","YEAR"]).sum()
           /pnum.groupby(["RUN","YEAR"]).sum()
           * 10**6)
    agg["REGION"] = "GB"
    agg = agg.reset_index().set_index(["RUN","REGION","YEAR"])
    data[0]["CostPerDomProp"] = pd.concat([data[0]["CostPerDomProp"],
                                           agg])
    print(data[0]["CostPerDomProp"])
    data[0]["CostPerDomProp"].loc[:,"VALUE"] = data[0]["CostPerDomProp"].loc[:,"VALUE"].multiply(xscale,
                                                                   axis=0)
    data[0]["CostPerDomHeat"].loc[:,"VALUE"] = data[0]["CostPerDomHeat"].loc[:,"VALUE"].multiply(xscale,
                                                                   axis=0)

    plot_data_11 = data[0]["CostPerDomProp"].loc[data[0]["CostPerDomProp"].index.get_level_values("YEAR")<2060].reset_index()
    plot_data_12 = data[0]["CostPerDomHeat"].loc[data[0]["CostPerDomHeat"].index.get_level_values("YEAR")<2060].reset_index()
    # model.results[0]["CostPerDomPropGDHI"] = (model.results[0]["CostPerDomProp"]
    #                                           .divide(gdhi["2021"],level=1,axis=0)
    #                                           .dropna())
    # model.results[0]["GDHI"] = model.results[0]["CostPerDomPropGDHI"].copy()
    # model.results[0]["GDHI"].loc[:,"VALUE"] = 1
    # model.results[0]["GDHI"] = (model.results[0]["GDHI"]
    #                             .multiply(gdhi["2021"],level=1,axis=0))
    
    
    
    # save data
    plot_data_11.to_csv(dpath+"plot_data_11.csv", index=False)
    plot_data_11.loc[:,"REGION"] = plot_data_11.loc[:,"REGION"].map(mapping)
    plot_data_11.to_csv(dpath+"plot_data_11n.csv", index=False)
    
    plot_data_12.to_csv(dpath+"plot_data_12.csv", index=False)
    plot_data_12.loc[:,"REGION"] = plot_data_12.loc[:,"REGION"].map(mapping)
    plot_data_12.to_csv(dpath+"plot_data_12n.csv", index=False) 

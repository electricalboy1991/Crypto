for ii in Kimplist:
    if myUpbit.IsHasCoin(balance_upbit, ii) == False:
        del Krate_ExClose[ii]
        del Krate_total[ii]
        del Situation_flag[ii]
        Kimplist.remove(ii)

        with open(Krate_ExClose_type_file_path, 'w') as outfile:
            json.dump(Krate_ExClose, outfile)
        with open(Krate_total_type_file_path, 'w') as outfile:
            json.dump(Krate_total, outfile)
        with open(Situation_flag_type_file_path, 'w') as outfile:
            json.dump(Situation_flag, outfile)
        with open(Kimplist_type_file_path, 'w') as outfile:
            json.dump(Kimplist, outfile)
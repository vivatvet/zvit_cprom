import pprint

import pandas as pd
import argparse


class Run:

    def __init__(self):
        # /home/vladimir/PycharmProjects/zvit_cprom/zv_cprom.xlsx
        self.data = pd.read_excel(commands.file, sheet_name=0)
        self.sum_groups = {}

    def get_tv_list(self):
        tv_list = []
        for index, k in self.data.iterrows():
            tv_list.append(k["TV"])
        tv_list = sorted(list(set(tv_list)))
        return tv_list

    def calculation_ind_bsind(self):
        ind_list = []
        bsind_list = []
        for i, v in self.data.iterrows():
            res_ind = v["CO"] / v["CP"] * 100
            res_bsind = v["BS"] * res_ind / 100
            ind_list.append(res_ind)
            bsind_list.append(res_bsind)
        self.data["ind"] = ind_list
        self.data["BS_ind"] = bsind_list

    def add_sum_by_tv(self, tv_list) -> pd.DataFrame:
        sum_bs_by_tv = self.data.groupby(by="TV").sum()["BS"]
        sum_bsind_by_tv = self.data.groupby(by="TV").sum()["BS_ind"]
        result_data = self.data[self.data["TV"] == tv_list[0]]
        row = {"TV": tv_list[0], "BS": sum_bs_by_tv[tv_list[0]], "ind": sum_bsind_by_tv[tv_list[0]] / sum_bs_by_tv[tv_list[0]] * 100, "BS_ind": sum_bsind_by_tv[tv_list[0]]}
        result_data = pd.concat([result_data, pd.DataFrame(row, index=[0])], ignore_index=True)
        first = True
        for tv in tv_list:
            if first:
                first = False
                continue
            tem = self.data[self.data["TV"] == tv]
            row = {"TV": tv, "BS": sum_bs_by_tv[tv], "ind": sum_bsind_by_tv[tv] / sum_bs_by_tv[tv] * 100, "BS_ind": sum_bsind_by_tv[tv]}
            ptem = pd.concat([tem, pd.DataFrame(row, index=[0])], ignore_index=True)
            result_data = pd.concat([result_data, ptem], ignore_index=True)
        return result_data

    @staticmethod
    def add_sum_by_six_tv(df, tv_list):
        result_data = None
        tv_six_list_raw = [".".join(v.split(".")[0:3]) for v in tv_list]
        tv_six_list = []
        tmp = []
        for k in tv_six_list_raw:
            if k not in tmp:
                tv_six_list.append(k)
            tmp.append(k)
        first = True
        for tv_six in tv_six_list:
            st = tv_six + '.*'
            group_tv = df[df["TV"].str.match(st)]
            group_by_sum_tv = group_tv[group_tv["SEK"].isna()]
            sum_bs_group_tv = group_by_sum_tv.sum()["BS"]
            sum_bsind_group_tv = group_by_sum_tv.sum()["BS_ind"]
            row = {
                "TV": tv_six,
                "BS": sum_bs_group_tv,
                "ind": sum_bsind_group_tv / sum_bs_group_tv * 100,
                "BS_ind": sum_bsind_group_tv
            }
            if tv_six in tv_list:
                ptem = group_tv
            else:
                ptem = pd.concat([group_tv, pd.DataFrame(row, index=[0])], ignore_index=True)
            if first:
                result_data = ptem
                first = False
                continue
            result_data = pd.concat([result_data, ptem], ignore_index=True)
        return result_data, tv_six_list

    def add_sum_by_four_tv(self, df, tv_six_list):
        exclude = ['31.01','31.02', '31.03', '31.09', '31.00', '12.00']
        result_data = None
        tv_four_list_raw = [".".join(v.split(".")[0:2]) for v in tv_six_list]
        tv_four_list = []
        tmp = []
        for k in tv_four_list_raw:
            if k not in tmp:
                tv_four_list.append(k)
            tmp.append(k)
        first = True

        for tv_four in tv_four_list:
            st = tv_four + '.*'
            group_tv = df[df["TV"].str.match(st)]
            sum_bs_group_four_tv = self.data[self.data["TV"].str.match(st)].sum(numeric_only=True)["BS"]
            sum_bsind_group_four_tv = self.data[self.data["TV"].str.match(st)].sum(numeric_only=True)["BS_ind"]
            if tv_four not in exclude:
                row = {
                    "TV": tv_four,
                    "BS": sum_bs_group_four_tv,
                    "ind": sum_bsind_group_four_tv / sum_bs_group_four_tv * 100,
                    "BS_ind": sum_bsind_group_four_tv
                }
                ptem = pd.concat([group_tv, pd.DataFrame(row, index=[0])], ignore_index=True)
            else:
                ptem = group_tv
            if first:
                result_data = ptem
                first = False
                continue
            result_data = pd.concat([result_data, ptem], ignore_index=True)
        return result_data, tv_four_list

    def add_sum_by_three_tv(self, df, tv_four_list):
        result_data = None
        tv_three_list_raw = [v[0:4] for v in tv_four_list]
        tv_three_list = []
        tmp = []
        for k in tv_three_list_raw:
            if k not in tmp:
                tv_three_list.append(k)
            tmp.append(k)
        first = True
        for tv_thee in tv_three_list:
            st = tv_thee + '.*'
            st2 = tv_thee + '[1-9]'
            group_tv = df[df["TV"].str.match(st)]
            sum_bs_group_three_tv = self.data[self.data["TV"].str.match(st2)].sum(numeric_only=True)["BS"]
            sum_bsind_group_three_tv = self.data[self.data["TV"].str.match(st2)].sum(numeric_only=True)["BS_ind"]
            if sum_bs_group_three_tv != 0 and tv_thee[-1:] != "0":
                row = {
                    "TV": tv_thee,
                    "BS": sum_bs_group_three_tv,
                    "ind": sum_bsind_group_three_tv / sum_bs_group_three_tv * 100,
                    "BS_ind": sum_bsind_group_three_tv
                }
                ptem = pd.concat([group_tv, pd.DataFrame(row, index=[0])], ignore_index=True)
            else:
                ptem = group_tv
            if first:
                result_data = ptem
                first = False
                continue
            result_data = pd.concat([result_data, ptem], ignore_index=True)
        return result_data

    def add_sum_by_two_tv(self, df, tv_four_list):
        result_data = None
        tv_two_list_raw = [".".join(v.split(".")[0:1]) for v in tv_four_list]
        tv_two_list = []
        tmp = []
        for k in tv_two_list_raw:
            if k not in tmp:
                tv_two_list.append(k)
            tmp.append(k)
        first = True
        for tv_two in tv_two_list:
            st = tv_two + '.*'
            group_tv = df[df["TV"].str.match(st)]
            sum_bs_group_two_tv = self.data[self.data["TV"].str.match(st)].sum(numeric_only=True)["BS"]
            sum_bsind_group_two_tv = self.data[self.data["TV"].str.match(st)].sum(numeric_only=True)["BS_ind"]
            row = {
                "TV": tv_two,
                "BS": sum_bs_group_two_tv,
                "ind": sum_bsind_group_two_tv / sum_bs_group_two_tv * 100,
                "BS_ind": sum_bsind_group_two_tv
            }
            ptem = pd.concat([group_tv, pd.DataFrame(row, index=[0])], ignore_index=True)
            if first:
                result_data = ptem
                first = False
                continue
            result_data = pd.concat([result_data, ptem], ignore_index=True)
        return result_data

    def main(self):
        tv_list = self.get_tv_list()
        self.calculation_ind_bsind()
        result = self.add_sum_by_tv(tv_list=tv_list)
        six_result, tv_six_list = self.add_sum_by_six_tv(df=result, tv_list=tv_list)
        four_result, tv_four_list = self.add_sum_by_four_tv(df=six_result, tv_six_list=tv_six_list)
        three_result = self.add_sum_by_three_tv(df=four_result, tv_four_list=tv_four_list)
        two_result = self.add_sum_by_two_tv(df=three_result, tv_four_list=tv_four_list)
        input_file = commands.file
        output_file = input_file.split(".")[0] + "_modefined." + input_file.split(".")[1]
        two_result.to_excel(output_file)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(prog="zvcprom", add_help=False)
    args_parser.add_argument("--file")
    commands, args = args_parser.parse_known_args()
    if not commands.file:
        print("Use --file [path to file]")
        exit(1)
    Run().main()

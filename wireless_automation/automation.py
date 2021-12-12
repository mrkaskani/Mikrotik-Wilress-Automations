from collections import defaultdict
from wireless_automation import Authentication
import pandas as pd


class Automation(Authentication):
    """
    select the most free frequencies on 5Ghz band,
    IEEE 802.11n and 20/40 channel width with analysing spectral scan tool
    """

    def __init__(self, ip, username, password):
        super().__init__(ip, username, password)

    @staticmethod
    def _count_dot_colon(freq_power_graph: str) -> tuple:
        """
        count the dot and colon in graph for scalar analysis
        :param freq_power_graph: get string to count dot and colon
        :return number of dot and colon in graph in a tuple:
        """
        dot, colon = 0, 0
        for character in freq_power_graph:
            if character == '.':
                dot += 1
            elif character == ":":
                colon += 1
        return dot, colon

    def _scan(self) -> pd.DataFrame:
        """
        we have 4920 to 6100 frequency range in 5Ghz band and RouterOS has 200 buckets limitation per command,
        divide the range by 200 with "while loop" and run command to get data from "spectral scan" tool.
        at the end we grouped repetitious frequencies just as a key and its data as value in list with "defaultdict" collection
        :return convert dictionary to pandas dataframe to analysis data:

        sample command run on the RouterOS:
        "interface wireless spectral-scan number=0 range=4940-5100 buckets=200 duration=63"

        sample output:
              freq   dbm                                     graph .section
        0     4920  -103  .                                               3
        1     4921  -101  .                                               3
        2     4922   -99  .                                               3
        ...    ...   ...                                       ...      ...
        1197  6107  -101  .                                               3
        1198  6108  -100  .                                               3
        1199  6109  -103  .                                               3
        """
        grouped_default_dict = defaultdict(list)
        MIN_START_OF_BUCKET_RANGE, MIN_END_OF_BUCKET_RANGE = 4940, 5100
        MAX_START_OF_BUCKET_RANGE, MAX_END_SCAN_RANGE = 5940, 6100
        MIN_LAST_RANGE_TO_START, MAX_LAST_RANGE_TO_END = 5740, 5940
        NUMBER_TO_CREATE_NEXT_RANGE, NUMBER_TO_CREATE_NEXT_LAST_RANGE = 200, 140
        NUMBER_OF_BUCKETS, DURATION = '200', '4'

        with Authentication(ip=self.ip, username=self.username, password=self.password) as connection:
            while MIN_START_OF_BUCKET_RANGE <= MAX_START_OF_BUCKET_RANGE and MIN_END_OF_BUCKET_RANGE <= MAX_END_SCAN_RANGE:
                spectral_scan = connection.get_resource('/interface/wireless').call(
                    'spectral-scan', {
                        'number': '0',
                        'range': f'{MIN_START_OF_BUCKET_RANGE}-{MIN_END_OF_BUCKET_RANGE}',
                        'buckets': NUMBER_OF_BUCKETS,
                        'duration': DURATION,
                    },
                )
                if MIN_START_OF_BUCKET_RANGE == MIN_LAST_RANGE_TO_START and MIN_END_OF_BUCKET_RANGE == MAX_LAST_RANGE_TO_END:
                    MIN_START_OF_BUCKET_RANGE += NUMBER_TO_CREATE_NEXT_RANGE
                    MIN_END_OF_BUCKET_RANGE += NUMBER_TO_CREATE_NEXT_LAST_RANGE
                else:
                    MIN_START_OF_BUCKET_RANGE += NUMBER_TO_CREATE_NEXT_RANGE
                    MIN_END_OF_BUCKET_RANGE += NUMBER_TO_CREATE_NEXT_RANGE

                for frequency in spectral_scan:
                    if 'graph' in frequency.keys():
                        for key, value in frequency.items():
                            grouped_default_dict[key].append(value)
            return pd.DataFrame.from_dict(grouped_default_dict, orient='columns', )

    def _cleaning_freq_power_data(self) -> pd.DataFrame:
        """
        convert dot and colon in graph to scalar and add it as column to dataframe,
        for analysis data and cast it as a integer
        :return cleaned dataframe:

        sample output :
              freq  dbm                                     graph .section  dot  colon
        0     4920 -105  .                                               3    1      0
        1     4921 -102  .                                               3    1      0
        2     4922 -100  .                                               3    1      0
        ...    ...  ...                                       ...      ...  ...    ...
        1197  6107 -101  .                                               3    1      0
        1198  6108 -102  .                                               3    1      0
        1199  6109 -102  .                                               3    1      0
        """
        spectral_scan = self._scan()
        spectral_scan['dot'] = spectral_scan['graph'].apply(lambda x: self._count_dot_colon(x)[0])
        spectral_scan['colon'] = spectral_scan['graph'].apply(lambda x: self._count_dot_colon(x)[1])
        spectral_scan = spectral_scan.astype({'dbm': int, 'colon': int, 'dot': int})
        return spectral_scan

    def _analyse_freq_power_per_1mhz(self) -> pd.DataFrame:
        """
        calculate average and variance of grouped "frequency power" per 1 mhz
        remove unnecessary columns
        :return analysed data in pandas dataframe:
        sample output:
                     dbm     colon       dot   dbm_var  colon_var   dot_var
        freq
        4920 -104.466667  0.000000  1.000000  7.129893   1.341982  0.000484
        4921 -101.416667  0.000000  1.000000  7.129893   1.341982  0.000484
        4922  -99.350000  0.433333  1.050000  7.129893   1.341982  0.000484
        ...          ...       ...       ...       ...        ...       ...
        6107 -100.750000  0.000000  1.000000  7.129893   1.341982  0.000484
        6108 -100.800000  0.000000  1.000000  7.129893   1.341982  0.000484
        6109 -103.550000  0.000000  1.000000  7.129893   1.341982  0.000484
        """
        cleaned_data = self._cleaning_freq_power_data()
        analysed_data = cleaned_data.groupby('freq').agg({'dbm': 'mean', 'colon': 'mean', 'dot': 'mean', })
        analysed_data['dbm_var'] = analysed_data['dbm'].var()
        analysed_data['colon_var'] = analysed_data['colon'].var()
        analysed_data['dot_var'] = analysed_data['dot'].var()
        return analysed_data

    def _analyse_freq_power_per_40mhz(self) -> pd.DataFrame:
        """
        divide 1 Mhz analysed data to 40Mhz range with "while loop" to get maximum range of
        IEEE 802.11n and 20/40 channel width
        then calculate average and variance per its 40 range
        :return list of frequencies:

        sample output:
                     dbm   dbm_var  colon  colon_var       dot  dot_var
        4920  -99.243902  0.268293    1.0   7.569996  1.391662      0.0
        4925  -99.000000  0.292683    1.0   7.569996  1.391662      0.0
        4930  -98.878049  0.365854    1.0   7.569996  1.391662      0.0
        ...          ...       ...    ...        ...       ...      ...
        6045 -100.682927  0.024390    1.0   7.569996  1.391662      0.0
        6050 -100.682927  0.024390    1.0   7.569996  1.391662      0.0
        6055 -100.621951  0.024390    1.0   7.569996  1.391662      0.0
        """
        spectral_scan = self._analyse_freq_power_per_1mhz()
        START_iLOC, END_iLOC = 0, 41
        MAX_START_iLOC, MAX_END_iLOC = 1140, 1180
        dicts = {}
        while START_iLOC <= MAX_END_iLOC and END_iLOC <= MAX_END_iLOC:
            average = spectral_scan.iloc[START_iLOC: END_iLOC].mean()
            dicts[START_iLOC + 4920] = list(average)
            START_iLOC += 5
            END_iLOC += 5

        frequency_list = pd.DataFrame.from_dict(dicts,
                                                orient='index',
                                                columns=['dbm', 'dbm_var', 'colon', 'colon_var', 'dot', 'dot_var'])
        return frequency_list

    def _sorted_frequency(self) -> list:
        """
        :return:sorted data by lowest frequency useage power and cast it as list
        sample output:
        [5885, 5880, 5910, 5915, 5890,......, 5195, 5175, 5180, 5190, 5185]
        """
        frequencies = self._analyse_freq_power_per_40mhz()
        return list(frequencies.sort_values(by=['dbm', 'dbm_var', 'colon', 'colon_var', 'dot', 'dot_var']).index)

    def _select_frequency(self) -> list:
        """
        divide 5Ghz range by 100 and return best frequency in its range to use all of 5Ghz range
        :return list of frequencies:

        sample output:
        [4925, 5025, 5125, 5315, 5415, 5510, 5580, 5715, 5815, 5900, 5925, 6025]
        """
        mean_var_freq = self._sorted_frequency()
        freq_dict = {}
        freq_list = []
        MIN_START_FREQ_RANGE, MIN_END_FREQ_RANGE = 4920, 5020
        MAX_START_FREQ_RANGE, MAX_END_FREQ_RANGE = 6020, 6120

        while MIN_START_FREQ_RANGE <= MAX_START_FREQ_RANGE and MIN_END_FREQ_RANGE <= MAX_END_FREQ_RANGE:
            for freq in mean_var_freq:
                if MIN_START_FREQ_RANGE < freq < MIN_END_FREQ_RANGE:
                    freq_list.append(freq)
                    freq_dict[f"{MIN_START_FREQ_RANGE}-{MIN_END_FREQ_RANGE}"] = freq_list[0]
            MIN_START_FREQ_RANGE += 100
            MIN_END_FREQ_RANGE += 100
            freq_list.clear()
        return list(freq_dict.values())

    def set_freq(self):
        """
        convert integer frequency to string and join them with ',' character to standard RouterOS format

        sample command run on the RouterOS:
        interface wireless set number= 0 scan-list=4930,5025,5130,5300,5410,5515,5610,5715,5815,5910,5925,6025
        """
        scan_list = ",".join(map(str, self._select_frequency()))
        with Authentication(self.ip, self.username, self.password) as connection:
            set_freq = connection.get_resource('/interface/wireless').call(
                'set', {'scan-list': scan_list, 'numbers': '0'}
            )
        return set_freq

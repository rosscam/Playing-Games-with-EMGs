from main import IIRfilter
import unittest
import numpy as np
from scipy.signal import butter, sosfilt



class TestIIRFilter(unittest.TestCase):
        def test1(self):
            fs = 100.0 
            f1 = 10.0  

            sos = butter(2, f1 /fs*2, btype='low', output='sos')
        
            filter = IIRfilter(sos[0][0], sos[0][1], sos[0][2], sos[0][4], sos[0][5])

            # Generate the test signal
            t = np.linspace(0, 1.0, int(fs), endpoint=False) 
            input_signal = np.sin(2 * np.pi * 20 * t)
            
            
            filtered_signal = np.array([filter.filter(x) for x in input_signal])

            
            filtered_signal_reference = np.asarray([
                                        0.0, 0.06415378, 0.24128329, 0.3531023, 0.20018393, -0.08491164,
                                        -0.17968859, -0.00237213, 0.17526744, 0.09750349, -0.12886286, -0.18753734,
                                        0.00680005, 0.18899103, 0.109403, -0.12092708, -0.18337902, 0.00827701,
                                        0.18896261, 0.10876082, -0.12164934, -0.18393946, 0.00793459, 0.18880258,
                                        0.10871926, -0.12163078, -0.18390109, 0.00797078, 0.18882811, 0.1087335,
                                        -0.12162504, -0.18390042, 0.00796919, 0.18882601, 0.10873176, -0.12162617,
                                        -0.18390098, 0.00796901, 0.18882603, 0.10873186, -0.12162606, -0.1839009,
                                        0.00796906, 0.18882606, 0.10873187, -0.12162606, -0.18390091, 0.00796905,
                                        0.18882605, 0.10873187, -0.12162606, -0.18390091, 0.00796905, 0.18882605,
                                        0.10873187, -0.12162606, -0.18390091, 0.00796905, 0.18882605, 0.10873187,
                                        -0.12162606, -0.18390091, 0.00796905, 0.18882605, 0.10873187, -0.12162606,
                                        -0.18390091, 0.00796905, 0.18882605, 0.10873187, -0.12162606, -0.18390091,
                                        0.00796905, 0.18882605, 0.10873187, -0.12162606, -0.18390091, 0.00796905,
                                        0.18882605, 0.10873187, -0.12162606, -0.18390091, 0.00796905, 0.18882605,
                                        0.10873187, -0.12162606, -0.18390091, 0.00796905, 0.18882605, 0.10873187,
                                        -0.12162606, -0.18390091, 0.00796905, 0.18882605, 0.10873187, -0.12162606,
                                        -0.18390091, 0.00796905, 0.18882605, 0.10873187
                                    ])

            
            np.testing.assert_allclose(filtered_signal, filtered_signal_reference, atol=1e-8, rtol=1e-5,)
        
        def test2(self):
            fs = 100.0  
            f1 = 10.0   
            f2 = 30.0   

            
            sos = butter(2, [f1 / (fs / 2), f2 / (fs / 2)], btype='bandstop', output='sos')

            
            filter1 = IIRfilter(sos[0][0], sos[0][1], sos[0][2], sos[0][4], sos[0][5])
            filter2 = IIRfilter(sos[1][0], sos[1][1], sos[1][2], sos[1][4], sos[1][5])

            # Generate the test signal
            t = np.linspace(0, 1.0, int(fs), endpoint=False) 
            input_signal = np.sin(2 * np.pi * 20 * t)
                

            filtered_signal = np.array([filter1.filter(x) for x in input_signal])
            filtered_signal = np.array([filter2.filter(x) for x in filtered_signal])
            
            filtered_signal_reference = sosfilt(sos, input_signal)

            # Validate that the custom filter output matches scipy's sosfilt output
            np.testing.assert_allclose(filtered_signal, filtered_signal_reference, atol=1e-8, rtol=1e-5,)


if __name__ == "__main__":
    unittest.main()

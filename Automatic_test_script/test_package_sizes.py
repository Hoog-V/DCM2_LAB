import serial
import subprocess

#WiFi configuration
WiFi_SSID = 'SSID'
WiFi_Password = "PASSWORD"

# Needles for finding esp ip-addr in UART response
ip_search_str = "sta ip:"
ip_search_end_str = ", mask"

# Needles for finding bandwidth numbers in iperf output response
result_begin_str = "Bytes  "
result_end_str = "bits/sec"

# Setup command for initiating WiFi
Setup_CMD = "sta "+WiFi_SSID+" "+ WiFi_Password +"\r"

Initiate_server_CMD = "iperf -s\r"

def init_esp_iperf_server(s):
    s.write(Initiate_server_CMD.encode())

def run_local_iperf_instance(server_ip_addr, options):
    proc = subprocess.Popen(["iperf -c "+server_ip_addr+" "+options], stdout=subprocess.PIPE, shell=True)
    (output, err) = proc.communicate()
    outputstr = output.decode()
    return outputstr


def find_substring(src_str, begin_str, end_str):
    index = src_str.index(begin_str) + len(begin_str)
    index_stop = src_str.index(end_str)
    return src_str[index:index_stop]
    
def init_esp_wifi(ser):
    ser.write(Setup_CMD.encode())
    read_buffer_str = ""
    while(read_buffer_str.__contains__(", mask") == False):
          read_buffer = ser.read(200)
          read_buffer_str = read_buffer.decode('utf-8')
          print("Esp still has no ip")
    return find_substring(read_buffer_str, ip_search_str, ip_search_end_str)     
       
       
       
def main():
    ser = serial.Serial(
            # Serial Port to read the data from
            port='/dev/ttyUSB0',
 
            #Rate at which the information is shared to the communication channel
            baudrate = 115200,
   
            #Applying Parity Checking (none in this case)
            parity=serial.PARITY_NONE,
 
           # Pattern of Bits to be read
            stopbits=serial.STOPBITS_ONE,
        
            # Total number of bits to be read
            bytesize=serial.EIGHTBITS,
 
            # Number of serial commands to accept before timing out
            timeout=1
    )
    server_ip_addr = init_esp_wifi(ser)
    print(server_ip_addr)
    file1 = open("log.txt", "w")
    for i in range(0,5):
        init_esp_iperf_server(ser)
        outputstr = run_local_iperf_instance(server_ip_addr, "-t 5")
        print(outputstr)
        result = find_substring(outputstr, result_begin_str, result_end_str)
        file1.write(result+"\n")
    file1.close()

        
if __name__=="__main__":
    main()      

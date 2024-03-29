/**
 * This is the initial version of the the gclib Java wrapper. All functions are
 * subject to change in future releases of gclib.
 * 
 * Java hackers with recommendations on how to make this library better are
 * encouraged to email softwaresupport@galil.com. Somebody has to teach those
 * Galil Java noobs what's what.
 * 
 * Some identified "To Do" tasks:
 *   1. Synchronize access to Gclib and Gclibo interfaces.
 *   2. Choose a data structure to return GAddresses and GIpRequests.
 *   3. 
 */

package gclibjava;

import java.nio.charset.Charset; //Charset for string conversions

//JNA imports
import com.sun.jna.Library;
import com.sun.jna.Native;
import com.sun.jna.Pointer; //g
import com.sun.jna.ptr.PointerByReference; //for GCon* in GOpen()
import com.sun.jna.ptr.IntByReference; //for GSize* in GCommand()
import com.sun.jna.ptr.ByteByReference; //for GStatus* in GInterrupt()
import java.util.ArrayList;
import java.util.List; //List<Double>

/**
 * GclibJava uses Java Native Access (JNA) internally to wrap the gclib
 * functions in a Java-callable class. 
 */
public class GclibJava {
     
    Pointer gclibHandle; //handle for gclib's connection
    Boolean connected = false;  //we use a bool to indicate connection status
    byte[] trafficBuffer = new byte[524288]; //Most reads/writes to Galil hardware are small. This size will hold the largest array or program upload/download possible. 
        
    /**
     * Constructor adds gclib to JNA's path.
     */
    public GclibJava()
    {
        System.setProperty("jna.library.path", "C:\\Program Files (x86)\\Galil\\gclib\\dll\\x64");
    }

    /**
     * The last line of defense to close connection.
     * Do NOT rely on finalize(), call GClose() explicitly.
     * 
     * @throws Throwable super can throw.
     */
    @Override
    protected void finalize() throws Throwable
    {
        try {
            if (connected)
                GClose();
        } finally {
            super.finalize();
        }
    }  
    
    // -------------------------------------------------------------------------
    // JNA for gclib
    // -------------------------------------------------------------------------
    /**
     * The JNA interface to the gclib library.
     * http://galil.com/sw/pub/all/doc/gclib/html/gclib_8h.html
     */
    interface Gclib extends Library {
        Gclib INSTANCE = (Gclib)
                Native.loadLibrary("gclib",
                        Gclib.class);
        /* 
        Limit calls to one at a time
        Warning: gclibo library calls gclib. Therefore, calls to Gclib and
        Gclibo interfaces should not be concurrent.
        */
        Gclib SYNC_INSTANCE = (Gclib)
                Native.synchronizedLibrary(INSTANCE);
          
        int GArrayDownload(Pointer g, String arrayName, int first, int last, String buffer);
        int GArrayUpload(Pointer g, String arrayName, int first, int last, int delim, byte[] response, int len);
        int GCommand(Pointer g, String command, byte[] response, int len, IntByReference bytesReturned);
        int GClose(Pointer g);
        int GFirmwareDownload(Pointer g, String filePath);
        int GInterrupt(Pointer g, ByteByReference statusByte);
        int GMessage(Pointer g, byte[] response, int len);
        int GOpen(String address, PointerByReference g);
        int GProgramDownload(Pointer g, String program, String preprocessor);
        int GProgramUpload(Pointer g, byte[] response, int len);
    }
      
    // -------------------------------------------------------------------------
    // gclib functions
    // -------------------------------------------------------------------------
    
    /**
     * Downloads array data to a pre-dimensioned array in the controller's array table.
     * 
     * @param arrayName String containing the name of the array to download. Must match the array name used in DM.
     * 
     * @param data List containing the array data. The length of data may not be larger than the array dimensioned.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GArrayDownload(String arrayName, List<Double> data) throws GclibJavaException
    {
        String buf = new String();
        buf = data.stream().map((d) -> d.toString() + ",").reduce(buf, String::concat);
                        
        ec(Gclib.SYNC_INSTANCE.GArrayDownload(gclibHandle, arrayName, -1, -1, 
                buf.substring(0, buf.length() - 1)));//remove trailing comma       
    }    
    
    /**
     * Uploads array data from the controller's array table.
     * 
     * @param arrayName String containing the name of the array to upload.
     * 
     * @return A List of Doubles, containing the array data.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public List<Double> GArrayUpload(String arrayName) throws GclibJavaException
    {
        ec(Gclib.SYNC_INSTANCE.GArrayUpload(gclibHandle, arrayName, -1, -1, 1, trafficBuffer, trafficBuffer.length));
        String[] elements = cstringToString(trafficBuffer).split(", ");
        List<Double> doubleList = new ArrayList();
        for (String s : elements)
        {
            try
            {
                doubleList.add(Double.parseDouble(s));
            }
            catch (NumberFormatException e)
            {
                throw new GclibJavaException( -10002, e.getMessage()); //G_BAD_VALUE_RANGE
            }
        }
        return doubleList;             
    }
    
    /**
     * Closes a connection to a Galil Controller.
     */
    public void GClose()
    {
        Gclib.SYNC_INSTANCE.GClose(gclibHandle);
        connected = false;
    }
    
    /**
     * Performs a command-and-response transaction on the connection.
     * 
     * @param command command string to send to the controller. 
     * The library will append a carriage return to the command string.
     * 
     * @return The response from the controller. 
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public String GCommand(String command) throws GclibJavaException
    {
        IntByReference ptrInt = new IntByReference(); //for bytes read
        ec(Gclib.SYNC_INSTANCE.GCommand(gclibHandle, command, trafficBuffer, trafficBuffer.length, ptrInt));  
        String response = cstringToString(trafficBuffer);       
       
        int index = response.lastIndexOf("\r\n:");
        if (index > 0)
            response = response.substring(0, index); //trim trailing crlf:
        
        return response;        
    }
    
     /**
     * Upgrade firmware.
     * 
     * @param filePath The full file path to the Galil-supplied firmware hex 
     * file. See <a href="http://www.galil.com/downloads/firmware" target="_top">
     * http://www.galil.com/downloads/firmware
     * </a>
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GFirmwareDownload(String filePath) throws GclibJavaException
    {
        ec(Gclib.SYNC_INSTANCE.GFirmwareDownload(gclibHandle, filePath));
    }
    
    /**
     * Provides access to PCI and UDP interrupts from the controller.
     * 
     * Interrupts can be generated automatically by the firmware on important 
     * events via EI (Enable Interrupt) or by the user in embedded DMC code via
     * UI (User Interrupt). To use this function, -s EI must be used in the 
     * GOpen() address string to subscribe to interrupts.
     * 
     * @return The status byte of the interrupt.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public byte GInterrupt() throws GclibJavaException
    {
        ByteByReference statusByte = new ByteByReference();
        ec(Gclib.SYNC_INSTANCE.GInterrupt(gclibHandle, statusByte));
        return statusByte.getValue();    
    }
            
    /**
     * Provides access to unsolicited messages from the controller.
     * 
     * To use this function, -s MG must be used in the GOpen() address string to
     * subscribe to messages. Unsolicited bytes must be flagged by the high-bit 
     * setting, CW 1. The driver will automatically set this when subscribing to
     * messages. The user should not overwrite this setting.
     * 
     * Unsolicited messages are data generated by the controller that are not in
     * response to a command, a data record, or an interrupt.
     * 
     * GMessage() will block until a message is received, or the function times
     * out.
     * 
     * Messages are unframed byte streams. There is no guarantee that the user 
     * will get complete messages or single messages in a call to GMessage().
     * 
     * @return the message received.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public String GMessage() throws GclibJavaException
    {
        ec(Gclib.SYNC_INSTANCE.GMessage(gclibHandle, trafficBuffer, trafficBuffer.length));
        return cstringToString(trafficBuffer);          
    }
        
    /**
     * Open a connection to a Galil Controller.
     * 
     * @param address  address string. See 
     * <a href="http://galil.com/sw/pub/all/doc/gclib/html/gclib_8h_aef4aec8a85630eed029b7a46aea7db54.html#aef4aec8a85630eed029b7a46aea7db54" target="_top">
     * gclib GOpen()</a>
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GOpen(String address) throws GclibJavaException
    {
        if (connected)
            GClose();
        
        PointerByReference ptrRef = new PointerByReference();
        ec(Gclib.SYNC_INSTANCE.GOpen(address, ptrRef));
        gclibHandle = ptrRef.getValue();    
        connected = true;
    }
    
    /**
     * Downloads a program to the controller's program buffer.
     * 
     * @param program Program for download.
     * 
     * @param preprocessor Options string for preprocessing the program before sending it to the controller.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GProgramDownload(String program, String preprocessor) throws GclibJavaException
    {
        ec(Gclib.SYNC_INSTANCE.GProgramDownload(gclibHandle, program, preprocessor));
    }
    
    /**
     * Overload of GProgramDownload to use default preprocessor options.
     * 
     * @param program Program for download.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GProgramDownload(String program) throws GclibJavaException
    {
        GProgramDownload(program, "");
    }
   
    /**
     * Uploads a program from the controller's program buffer.
     * 
     * @return The uploaded program.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public String GProgramUpload() throws GclibJavaException
    {
        ec(Gclib.SYNC_INSTANCE.GProgramUpload(gclibHandle, trafficBuffer, trafficBuffer.length));
        return cstringToString(trafficBuffer);
    }
    
    // -------------------------------------------------------------------------
    // JNA for gclibo
    // -------------------------------------------------------------------------
    
     /**
     * The JNA interface to the open source, gclibo library.
     * http://galil.com/sw/pub/all/doc/gclib/html/gclibo_8h.html
     */
    interface Gclibo extends Library {
        Gclibo INSTANCE = (Gclibo)
            Native.loadLibrary("gclibo",
                               Gclibo.class);
       /* 
        Limit calls to one at a time
        Warning: gclibo library calls gclib. Therefore, calls to Gclib and
        Gclibo interfaces should not be concurrent.
        */
        Gclibo SYNC_INSTANCE = (Gclibo)
                Native.synchronizedLibrary(INSTANCE);
        
        int GAddresses(byte[] response, int len);
        int GArrayDownloadFile(Pointer g, String filePath);
        int GArrayUploadFile(Pointer g, String filePath, String names);
        int GAssign(String ip, String mac);
        void GError(int rc, byte[] response, int len);
        int GInfo(Pointer g, byte[] response, int len);
        int GIpRequests(byte[] response, int len);
        int GProgramDownloadFile(Pointer g, String filePath, String preprocessor);
        int GProgramUploadFile(Pointer g, String filePath);
        void GSleep(int timeout_ms);
        int GTimeout(Pointer g, short timeout_ms);
        int GVersion(byte[] response, int len);
        int GSetServer(String server_name);
        int GServerStatus(byte[] response, int len);
        int GListServers(byte[] response, int len);
        int GPublishServer(String server_name, int publish, int save);
        int GRemoteConnections(byte[] response, int len);
    }
    
    // -------------------------------------------------------------------------
    // gclibo functions
    // -------------------------------------------------------------------------
    
    /**
     * Uses GUtility(), G_UTIL_GCAPS_ADDRESSES or G_UTIL_ADDRESSES to provide a 
     * listing of all available connection addresses.
     * 
     * @return String containing the available addresses.
     * 
     * 10.1.3.91, DMC4020 Rev 1.2e, LAN, 10.1.3.10
     * 192.168.0.63, DMC4040 Rev 1.2f, Static, 192.168.0.41
     * (192.0.0.42), RIO47102 Rev 1.1j, Static, 192.168.0.41
     * 10.1., RIO47102 Rev 1.1j, Static, 192.168.0.41
     * GALILPCI1
     * COM1
     * COM2
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public String GAddresses() throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GAddresses(trafficBuffer, trafficBuffer.length));
        return cstringToString(trafficBuffer);                       
    }
    
    /**
     * Array download from file.
     * Downloads a csv file containing array data at file_path. If the arrays don't exist, they will be dimensioned.
     * 
     * @param filePath String containing the path to the array file.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GArrayDownloadFile(String filePath) throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GArrayDownloadFile(gclibHandle, filePath));
    }
    
    /**
     * Array upload to file.
     * Uploads the entire controller array table or a subset and saves the data
     * as a csv file specified by file_path.
     * 
     * @param filePath String containing the path to the array file. File will
     * be overwritten if it exists.
     * 
     * @param names String containing the arrays to upload, delimited with 
     * space. "" uploads all arrays listed in LA.
     * 
     * @throws gclibjava.GclibJavaException If an error is generated by gclib.
     */
    public void GArrayUploadFile(String filePath, String names) throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GArrayUploadFile(gclibHandle, filePath, names));
    }
    
    /**
     * Overload of GArrayUploadFile to upload all arrays.
     * 
     * @param filePath String containing the path to the array file. File will
     * be overwritten if it exists.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GArrayUploadFile(String filePath) throws GclibJavaException
    {
        GArrayUploadFile(filePath, "");
    }
    
    /**
     * Uses GUtility(), G_UTIL_GCAPS_ASSIGN or G_UTIL_ASSIGN to assign an IP
     * address over the Ethernet to a controller at a given MAC address.
     * 
     * @param ipAddress The IP address to assign.
     * 
     * @param macAddress The MAC address of the hardware.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GAssign(String ipAddress, String macAddress) throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GAssign(ipAddress, macAddress));
    }
    
    /**
     * Uses GUtility() and G_UTIL_INFO to provide a useful connection string.
     * 
     * @return A String containing the info, e.g. 
     * 192.168.0.42, DMC30010 Rev 1.2i, 6969
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public String GInfo() throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GInfo(gclibHandle, trafficBuffer, trafficBuffer.length));
        return cstringToString(trafficBuffer);        
    }
    
    /**
     * Uses GUtility(), G_UTIL_GCAPS_IPREQUEST or G_UTIL_IPREQUEST to provide a
     * list of all Galil controllers requesting IP addresses via BOOT-P or DHCP.
     * 
     * @return String containing hardware requesting IP addresses.
     * 
     * DMC4000, 291, 00:50:4C:20:01:23, LAN, 10.1.3.10
     * RIO47000, 37290, 00:50:4C:28:91:AA, Static, 192.168.0.41
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public String GIpRequests() throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GIpRequests(trafficBuffer, trafficBuffer.length));
        return cstringToString(trafficBuffer);     
    }
    
    /**
     * Program download from file.
     * 
     * @param filePath String containing the path to the program file.
     * 
     * @param preprocessor Options string for preprocessing the program before sending it to the controller.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GProgramDownloadFile(String filePath, String preprocessor) throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GProgramDownloadFile(gclibHandle, filePath, preprocessor));
    }
    
    /**
     * Overload of GProgramDownloadFile to use default preprocessor options.
     * 
     * @param filePath  String containing the path to the program file.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GProgramDownloadFile(String filePath) throws GclibJavaException
    {
        GProgramDownloadFile(filePath, "");
    }
    
    /**
     * Program upload to file.
     * 
     * @param filePath String containing the path to the program file, 
     * file will be overwritten if it exists.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GProgramUploadFile(String filePath) throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GProgramUploadFile(gclibHandle, filePath));
    }
    
    /**
     * Uses GUtility() and G_UTIL_SLEEP to provide a blocking sleep call which 
     * can be useful for timing-based chores.
     * 
     * In GclibJava, this is primarily a debugging call.
     * 
     * @param timeout_ms Sleep time in milliseconds.
     */
    public void GSleep(int timeout_ms)
    {        
        Gclibo.SYNC_INSTANCE.GSleep(timeout_ms);    
    }
    
    /**
     * Uses GUtility() and G_UTIL_TIMEOUT_OVERRIDE to set the library timeout.
     * 
     * @param timeout_ms The value to be used for the timeout. Use -1 to set the
     * timeout back to the initial GOpen() value, --timeout.
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public void GTimeout(short timeout_ms) throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GTimeout(gclibHandle, timeout_ms));
    }
    
     /**
     * Uses GUtility(), G_UTIL_VERSION and G_UTIL_GCAPS_VERSION to provide the 
     * library and gcaps version numbers.
     * 
     * @return A String containing the version, e.g. 
     * 189.224.370 1.0.0.125
     * 
     * @throws GclibJavaException If an error is generated by gclib.
     */
    public String GVersion() throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GVersion(trafficBuffer, trafficBuffer.length));
        return cstringToString(trafficBuffer);        
    } 
    
    /** 
    * Connects gclib to a new gcaps server
    * 
    * @param server_name Name to publish server under.
    * 
    * @throws GclibJavaException If an error is generated by gclib.
    */
    public void GSetServer(String server_name) throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GSetServer(server_name));
    }
    
    /** 
    * Retrieves the name of your local gcaps server and whether or not it is currently published
    * Retrieves a list of gcaps servers that are advertising themselves on the local network.
    * 
    * @returns A string in the form "<server_name>, <isPublished>"
    * 
    * @throws GclibJavaException If an error is generated by gclib.
    */    
    public String GServerStatus() throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GServerStatus(trafficBuffer, trafficBuffer.length));
        return cstringToString(trafficBuffer); 
    }
    
    /** 
    * Retrieves a list of gcaps servers that are advertising themselves on the local network.
    * 
    * @returns A list of available gcaps server names.
    * 
    * @throws GclibJavaException If an error is generated by gclib.
    */
    public String GListServers() throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GListServers(trafficBuffer, trafficBuffer.length));
        return cstringToString(trafficBuffer);  
    }
    
    /** 
    * Publishes or removes local gcaps server from the network
    * 
    * @param server_name Name to publish server under.
    * @param publish True=publish server, False=remove server.
    * @param save Save this configuration for future server reboots.
    * 
    * @throws GclibJavaException If an error is generated by gclib.
    */
    public void GPublishServer(String server_name, int publish, int save) throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GPublishServer(server_name, publish, save));
    }
    
    /** 
    * Returns a list of IP Addresses that currently have an open connection to your hardware.
    * 
    * @returns a list of IP Addresses that currently have an open connection to your hardware.
    * 
    * @throws GclibJavaException If an error is generated by gclib.
    */
    public String GRemoteConnections() throws GclibJavaException
    {
        ec(Gclibo.SYNC_INSTANCE.GRemoteConnections(trafficBuffer, trafficBuffer.length));
        return cstringToString(trafficBuffer);  
    }
    
    // -------------------------------------------------------------------------
    // Helper functions
    // -------------------------------------------------------------------------
    
    //convert gclib's C strings to Java strings.
    String cstringToString(byte[] cbuf)
    {
        Charset charset = Charset.forName("UTF-8");
        int i;
        for (i = 0; i < cbuf.length && cbuf[i] != 0; i++){}//search for gclib's null terminator
        return new String(cbuf, 0, i, charset);    
    }
    
    //Error checker for gclib return code
    void ec(int returnCode) throws GclibJavaException
    {
        if (returnCode != 0)
        {
            //lookup human-readable string
            Gclibo.SYNC_INSTANCE.GError(returnCode, trafficBuffer, trafficBuffer.length);
            throw new GclibJavaException(returnCode, cstringToString(trafficBuffer));
        }
    }
    
}

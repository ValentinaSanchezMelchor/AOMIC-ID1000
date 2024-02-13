from socket import timeout
import requests
import asyncio
import aiohttp
import time
import gzip
import shutil
import os

urls = []
fns = []

#Settings--
limit = 15 #number of concurrent downloads
itemtodownload = 928 #number of entries
deleteraw = 1 #delete raw file once unzipped?


semaphore = asyncio.Semaphore(limit)

#statistics
totalsize = 0
starttime = 0
mbps = 0
downloaded = 0
started = 0


#generate a list of Urls and filenames
def generateURLS():
    for i in range(1,itemtodownload+1):
        padnum = str(i).zfill(3)
        link = f"https://s3.amazonaws.com/openneuro.org/ds003097/sub-0{padnum}/func/sub-0{padnum}_task-moviewatching_bold.nii.gz"
        fn = "sub-0"+padnum+"_task-moviewatching_bold.nii.gz"
        urls.append(link)
        fns.append(fn)


#async background task for downloading a file.
async def downloadfiles(url,filename):
    #limit concurrent downloads
    async with semaphore:
        global started
        started +=1
        #print(f"{started}/{itemtodownload} - Start file {filename}")
        #start a download
        async with aiohttp.ClientSession() as session:
            async with session.get(url,timeout = None) as response:
                #write file -  async wait for chunks and break on no more chunks
                with open(filename, mode="wb") as file:
                    while True:
                        try:
                            chunk = await response.content.read()
                        except Exception as e:
                            print(f"---- Error Downloading: {filename}")
                        if not chunk:
                            #calculate statistics
                            global totalsize,mbps,starttime,downloaded
                            StatisticUpdate(file.tell())
                            #end of file
                            break
                        #write a recieved chunk
                        file.write(chunk)
                    print(f"{downloaded}/{itemtodownload} - Downloaded file: {filename} - Average Speed: {mbps:.2f} Mbps")


def StatisticUpdate(size):
    global totalsize,mbps,starttime,downloaded
    totalsize = totalsize + size
    mbps = (totalsize*8/(1024.0*1024.0))/(time.perf_counter() - starttime)
    downloaded+=1 

def GZUnzipAll():
    for fn in fns:
        GZUnzipper("Raw/" + fn,"Unzipped/" + fn[:-3])
        

def GZUnzipper(filename_in,filename_out): 
    #statistics
    global started
    started+=1
    #print(f"{started}/{itemtodownload} - Start file {filename_in}")
    failed = False
    with gzip.open(filename_in, 'rb') as file_in:
        with open(filename_out, 'wb') as file_out:
            try:
                shutil.copyfileobj(file_in, file_out)
            except Exception as e:
                failed = True
            
            #statistics
            global totalsize,mbps,starttime,downloaded
            StatisticUpdate(file_out.tell())
            print(f"{downloaded}/{itemtodownload} - Unzipped file: {filename_out} - Average Speed: {mbps:.2f} Mbps")
    if failed:
        os.remove(filename_out)
    if deleteraw:
        os.remove(filename_in)
            
        

async def main():
    #make directories
    if not os.path.exists("Unzipped"):
        os.makedirs("Unzipped")    
    if not os.path.exists("Raw"):
        os.makedirs("Raw")    


    #generate Urls
    print ("Generating URLs")
    generateURLS()
    
    #setup statistics
    global totalsize,starttime,mbps,started,downloaded
    starttime = time.perf_counter()
    
    print ("Downloading Files")
    #generate tasks
    tasks = [downloadfiles(urls[i],"Raw/" + fns[i]) for i in range(0,itemtodownload)]
    
    #wait until all complete
    # await asyncio.wait_for(asyncio.gather(*tasks), timeout = None)
    await asyncio.gather(*tasks,return_exceptions=True)
    
    #print final statistics
    print(f"Downloaded: {(totalsize/(1024.0*1024.0)):.2f} Megabytes in {(time.perf_counter() - starttime):.2f} seconds at a speed of {mbps:.2f} Mbps" )
    print("")
    
    #unzip
    #setup statistics
    started = 0
    totalsize = 0
    downloaded = 0
    starttime = time.perf_counter()
    GZUnzipAll()
    
    print(f"Unzipped: {(totalsize/(1024.0*1024.0)):.2f} Megabytes in {(time.perf_counter() - starttime):.2f} seconds at a speed of {mbps:.2f} Mbps" )
    print("")
    

asyncio.run(main())
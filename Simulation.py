import math

import FTL
import SSD_Exceptions
import Statistics as st
import FTL_GROUP


def calculate_capacity(fname):
    lba_set = set()
    with open(fname, 'r') as f:
        f.readline()
        
        for line in f.readlines():
            lba, _, _, _ = map(int, line.split())
            
            lba_set.add(lba)

    return (1 + (len(lba_set) / st.PAGES_PER_BLOCK) * (1 + st.OVER_PROVISIONING_SPACE))



def simulation(fname, page_size, pages_per_block, blocks_per_ssd, gc_threshold, ops, num_wp):
    # SSD = FTL.FTL(page_size, pages_per_block, blocks_per_ssd, gc_threshold, ops)

    SSD_MLDT = FTL_GROUP.MLDT(page_size, pages_per_block, blocks_per_ssd, gc_threshold, ops, num_wp)

    with open(fname, 'r') as f:
        f.readline()
        for line in f.readlines():
            lba, size, dt, dt_per = map(int, line.split())
            
            try:
                if dt_per == -1:
                    dt_per = st.GROUP_NUMBER_COUNT - 1
                SSD_MLDT.write(lba, size, dt_per)
                
            except SSD_Exceptions.CapacityException as e:
                print(e)
                exit(1)
    
    print('Simulation Result')
    print(f'Write Requests : {st.WRITE_REQUEST_COUNT}')
    print(f'WAF : {(sum(st.GC_WRITE) + st.USER_WRITE) / st.USER_WRITE}')
    for i in range(st.GROUP_NUMBER_COUNT + 1):
        print(f'DT{i} valid page count : {st.GC_WRITE[i]}')


            



if __name__ == '__main__':
    # st.BLOCKS_PER_SSD = math.ceil(calculate_capacity(st.FNAME)) * 10
    simulation(st.FNAME, st.PAGE_SIZE, st.PAGES_PER_BLOCK, st.BLOCKS_PER_SSD, st.GC_TRHESHOLD, st.OVER_PROVISIONING_SPACE, st.NUM_WP)
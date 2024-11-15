import math

from collections import deque

import FTL
import SSD_Exceptions
import Block
import Statistics as st

class MLDT:
    
    def __init__(self, page_size, pages_per_block, blocks_per_ssd, gc_threshold, ops, num_wp):
        
        self.page_size = page_size
        self.pages_per_block = pages_per_block
        self.blocks_per_ssd = blocks_per_ssd
        self.capacity = page_size * pages_per_block * blocks_per_ssd

        self.gc_threshold = gc_threshold
        self.ops = ops
        self.num_wp = num_wp
        self.free_block_count = blocks_per_ssd

        self.blocks = [Block.Block(pages_per_block, i) for i in range(blocks_per_ssd)]

        self.free_block_que = deque([i for i in range(blocks_per_ssd)])
        self.sealed_block_que = deque([])

        self.write_pointer = [self.allocate_block() for _ in range(num_wp + 1)]

        for i in self.write_pointer:
            self.blocks[i].death_time_original = i

        # Values for Mapping LBA to ppn
        self.lpn_que = deque([i for i in range(blocks_per_ssd * pages_per_block)])

        self.lba_to_lpn = dict()
        self.lpn_to_ppn = dict()

        self.ppn_to_lpn = dict()
        self.lpn_to_lba = dict()

        print('Start SSD simulation with ' + st.FNAME + ' trace.')
        print('Prameters')
        print(f'Page Size : {self.page_size}')
        print(f'Pages Per Block : {self.pages_per_block}')
        print(f'Blocks Per SSD : {self.blocks_per_ssd}')
        print(f'SSD Capacity : {self.capacity / 1024 / 1024 / 1024} Giga Bytes')
        print(f'GC Threshold : {self.gc_threshold}')
        print(f'Over Provisioning Space : {self.ops}')
        print('-' * 50)
        
    def allocate_block(self):
        self.free_block_count -= 1

        return self.free_block_que.popleft()


    def write(self, lba, size, dt_per):
        while (self.free_block_count) < (self.blocks_per_ssd * (1 - self.gc_threshold * (1 - self.ops))):
            self.garbage_collection()

        # 해당 LBA가 사용된 적이 있는 경우, 할당된 lpn과 ppn을 삭제
        # If LBA has been used, remove allocated lpn and ppn
        if lba in self.lba_to_lpn:
            for lpn in self.lba_to_lpn[lba]:
                self.lpn_que.append(lpn)

                ppn = self.lpn_to_ppn[lpn]

                self.blocks[ppn // self.pages_per_block].invalidate_page(ppn)

                self.ppn_to_lpn.pop(ppn)
                self.lpn_to_ppn.pop(lpn)
                self.lpn_to_lba.pop(lpn)

            self.lba_to_lpn.pop(lba)

        page_count = math.ceil(size / self.page_size)

        self.lba_to_lpn[lba] = [self.lpn_que.popleft() for _ in range(page_count)]

        for lpn in self.lba_to_lpn[lba]:

            self.lpn_to_lba[lpn] = lba
            
            self.write_page(lpn, dt_per)
            st.USER_WRITE += 1

    def write_page(self, lpn, dt_per):
        blk_write_pointer, page_id = self.blocks[self.write_pointer[dt_per]].write_page()

        self.lpn_to_ppn[lpn] = page_id
        self.ppn_to_lpn[page_id] = lpn

        if blk_write_pointer == self.pages_per_block - 1:
            self.sealed_block_que.append(self.write_pointer[dt_per])
            self.write_pointer[dt_per] = self.allocate_block()
            self.blocks[self.write_pointer[dt_per]].death_time_original = dt_per

    def garbage_collection(self):
        victim = self.select_victim()
        self.free_block_que.append(victim)
        self.free_block_count += 1

        for ppn in self.blocks[victim].delete_block():
            self.gc_write(self.ppn_to_lpn[ppn], self.blocks[victim].death_time_original)
    
    def gc_write(self, lpn, dt_per):
        st.GC_WRITE[dt_per] += 1
        self.write_page(lpn, st.GROUP_NUMBER_COUNT)

    def select_victim(self):
        return self.sealed_block_que.popleft()


class Heap:
    """大顶堆"""

    def __init__(self, nums: [int]):
        super(Heap, self).__init__()
        self.nums = nums
        self.size = len(nums)
        self._heapify()

    # 删除堆顶元素
    def remove(self) -> int:
        if self.size == 0:
            return
        val = self.nums[0]
        self.nums[0] = self.nums[self.size - 1]
        self._siftDown(0)
        self.size -= 1
        return val

    # 批量建堆
    def _heapify(self):
        # 从非叶子节点开始下虑
        index = (self.size >> 1) - 1
        while index >= 0:
            self._siftDown(index)
            index -= 1

    # 下虑指定元素
    def _siftDown(self, index: int):
        curValue = self.nums[index]
        while index < (self.size >> 1):
            # 左子节点索引
            leftChildIndex = (index << 1) + 1
            # 右子节点索引
            rightChildIndex = leftChildIndex + 1

            # 默认左子节点最大
            maxChildIndex = leftChildIndex
            if rightChildIndex < self.size and self.nums[leftChildIndex] < self.nums[rightChildIndex]:
                maxChildIndex = rightChildIndex

            # 如果当前节点大于子节点则什么都不做
            if self.nums[maxChildIndex] < curValue:
                break

            # 将子节点覆盖当前节点的值
            self.nums[index] = self.nums[maxChildIndex]
            # 对较大的子节点继续进行下虑操作
            index = maxChildIndex

        # 将最初index的值赋值到它该待的位置
        self.nums[index] = curValue


if __name__ == '__main__':
    heap = Heap([0, 1, 2, 3, 4, 5, 9, 10, 7, 6, 8])
    heap.remove()

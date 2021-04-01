
class Sort:
    """经典排序算法"""

    def __init__(self):
        super(Sort, self).__init__()

    def sortArray(self, nums: [int]) -> [int]:
        if len(nums) < 2:
            return nums

        return self.heapSort(nums)

    # 堆排序 O(nlogN)
    def heapSort(self, nums: [int]) -> [int]:
        # 原地批量建堆
        heap = Heap(nums)

        # 依次拿出堆顶元素放到数组的最后面
        while heap.size > 0:
            top = heap.remove()
            nums[heap.size] = top
        return nums

    # 希尔排序

    def shellSort(self, nums: [int]) -> [int]:
        steps = self._shellSortSteps(nums)
        for step in steps:
            col = 0
            row = (len(nums) + step - 1) // step

            while col < step:  # 对当前列排序
                end = row
                while end > 0:
                    ri = 0
                    while ri < row:
                        curIndex = col + ri * step
                        nextIndex = col + (ri + 1) * step
                        if nextIndex < len(nums) and nums[curIndex] > nums[nextIndex]:
                            tmp = nums[curIndex]
                            nums[curIndex] = nums[nextIndex]
                            nums[nextIndex] = tmp
                        ri += 1
                    end -= 1
                col += 1

        return nums

    # 求shell排序的步长数组

    def _shellSortSteps(self, nums: [int]) -> [int]:
        steps = []
        count = len(nums)
        while (count >> 1) > 0:
            steps.append(count >> 1)
            count = count >> 1
        return steps

    # 归并排序 O(nlogN)
    def mergeSort(self, nums: [int], start: int, end: int) -> [int]:
        if end - start < 2:
            return
        # 核心思想： 先对左边归并排序再对右边归并排序，然后将左边和右边归并排序的结果合并起来
        mid = (start + end) >> 1
        self.mergeSort(nums, start, mid)
        self.mergeSort(nums, mid, end)  # 注意这个地方是mid 不是mid+1
        self._unionArray(nums, start, mid, end)

        return nums

    # 合并两个有序数组
    def _unionArray(self, nums: [int], start, mid, end):
        copyedLeftArray = nums[start: mid]
        li = 0
        ri = mid
        # print(copyedLeftArray, nums)
        while li < len(copyedLeftArray) and ri < end:
            if copyedLeftArray[li] > nums[ri]:
                nums[start] = nums[ri]
                ri += 1
            else:
                nums[start] = copyedLeftArray[li]
                li += 1
            start += 1

        # 将左边数组剩余的元素copy到排序数组的末尾
        while li < len(copyedLeftArray):
            nums[start] = copyedLeftArray[li]
            li += 1
            start += 1

    # 快速排序O(nlogN)
    def quickSort(self, nums: [int], start: int, end: int) -> [int]:
        if end - start < 2:
            return
        anchorIndex = self._findAnchorIndex(nums, start, end)
        self.quickSort(nums, start, anchorIndex)
        self.quickSort(nums, anchorIndex + 1, end)
        return nums

    # 找到快速排序的猫点
    def _findAnchorIndex(self, nums: [int], start: int, end: int) -> int:
        anchorVal = nums[start]
        curIndex = start

        while start < end:
            # 从右往左扫描
            while start < end:
                end -= 1
                if nums[end] < anchorVal:
                    nums[curIndex] = nums[end]
                    curIndex = end
                    break
            # 从左往右扫描
            while start < end:
                if nums[start] > anchorVal:
                    nums[curIndex] = nums[start]
                    curIndex = start
                    break
                start += 1
        nums[curIndex] = anchorVal
        return curIndex

    # 插入排序O(n^2)
    def insertionSort(self, nums: [int]) -> [int]:
        cur = 1
        while cur < len(nums):
            curValue = nums[cur]
            insertIndex = 0
            # 找到插入位置
            # while insertIndex <= cur and curValue > nums[insertIndex]:
            #     insertIndex += 1
            insertIndex = self._findInsertIndex(nums, 0, cur, curValue)
            # 将插入位置之后的元素依次往后移动
            moveIndex = cur - 1
            while moveIndex >= insertIndex:
                nums[moveIndex + 1] = nums[moveIndex]
                moveIndex -= 1

            # 将当前待排序元素插入正确位置
            nums[insertIndex] = curValue
            cur += 1
        return nums

    # 二分查找插入位置
    def _findInsertIndex(self, nums: [int], start: int, end: int, value: int) -> int:
        while start < end:
            mid = (start + end) >> 1
            if nums[mid] < value:
                start = mid + 1
            elif nums[mid] > value:
                end = mid
            else:
                return mid
        return start

    # 选择排序 O(n^2)
    def selectionSort(self, nums: [int]) -> [int]:
        end = len(nums)

        while end > 0:
            maxIndex = cur = 0
            while cur < end:
                if nums[cur] > nums[maxIndex]:
                    maxIndex = cur
                cur += 1
            # 找到最大值，然后将最大值和最后一个交换
            tmp = nums[end - 1]
            nums[end - 1] = nums[maxIndex]
            nums[maxIndex] = tmp

            end -= 1
        return nums

    # 冒泡排序 O(n^2)
    def bubbleSort(self, nums: [int]) -> [int]:
        end = lastExchangeIndex = len(nums)
        while end > 0:
            cur = 0
            end = min(end - 1, lastExchangeIndex)
            # 一轮循环
            while cur < end:
                if nums[cur] > nums[cur + 1]:
                    tmp = nums[cur]
                    nums[cur] = nums[cur + 1]
                    nums[cur + 1] = tmp

                    lastExchangeIndex = cur

                cur += 1
            # 如果一轮循环结束，一次交换都没有发生，则说明数组本身有序 直接返回
            if lastExchangeIndex == len(nums):
                return nums
        return nums


class Heap:
    """docstring for Heap"""

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
    sort = Sort()
    print(sort.sortArray([4, 6, 3, 2, 6, 9, 0, 6, 5, 4, 3, 3, 6, 8, 5, 4]))

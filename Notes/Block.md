# Block 本质
---

## Block底层实现
  
  * oc代码在编译时会转换成对应的c++的代码，我们可以使用如下命令将oc代码编译成c++代码，从而窥探block的本质：  
  `xcrun -sdk iphoneos clang -arch arm64 -rewrite-objc -fobjc-arc -fobjc-runtime=ios-12.0.0 main.m`
  
  * 例如将如下代码编译成c++代码
  ``` objc
  void testBlock() {
    void(^block)(void) = ^{
        NSLog(@"i am a block");
    };
  }
  ```
  对应c++实现：
  ``` c++
  
   // oc block的本质 就是一个结构体
   struct __testBlock_block_impl_0 { 
   struct __block_impl impl;
   struct __testBlock_block_desc_0* Desc;
   
   // 相当于block的构造方法，接收block的实现方法地址和block的描述两个参数
   __testBlock_block_impl_0(void *fp, struct __testBlock_block_desc_0 *desc, int flags=0) {
      impl.isa = &_NSConcreteStackBlock;
      impl.Flags = flags;
      impl.FuncPtr = fp;
      Desc = desc;
    }
  };
  
  // block 的实现 也就是oc block 中{}里面的代码
  static void __testBlock_block_func_0(struct __testBlock_block_impl_0 *__cself) { 
      NSLog((NSString *)&__NSConstantStringImpl__var_folders_6__qrgykwmd2_g_zcqhyrtwzr240000gn_T_main1_aa3ecf_mi_1);
  }
  
  // block的描述信息
  static struct __testBlock_block_desc_0 { 
      size_t reserved;
      size_t Block_size;
  } __testBlock_block_desc_0_DATA = { 0, sizeof(struct __testBlock_block_impl_0)};
  
  // 对应oc中的testBlock方法
  void testBlock() { 
      // 当我们定义一个oc的block时，本质上是定义了一个__testBlock_block_impl_0类型的结构体
      // 下面代码是将block的实现__testBlock_block_func_0和block的描述信息__testBlock_block_desc_0_DATA 
      // 传递给__testBlock_block_impl_0结构体从而创建block变量
      void(*block)(void) = ((void (*)())&__testBlock_block_impl_0((void *)__testBlock_block_func_0, &__testBlock_block_desc_0_DATA));
  }
   
  ```
  从上面代码可以看出 **block** 的底层实现其实是一个 **__testBlock_block_impl_0** 的结构体，当我们定义一个block时，实际上时创建了一个对应的结构体变量，该结构体接受两个参数 **fp** 和 **desc** 分别将block的*实现方法*和block的*描述信息*传给该结构体

## block中引用变量

  ```objc
  int c = 4;
  void testBlock() {
      int a = 3;
      static int b = 5;
      void(^block)(void) = ^{
          NSLog(@"%d %d %d",a, b , c);
      };
  }
  ```
  
  对应c++实现：
  
  ```c++
  int c = 4;

  struct __testBlock_block_impl_0 {
    struct __block_impl impl;
    struct __testBlock_block_desc_0* Desc;
    
    // 结构体内部会新增两个变量保存传递过来的a和b的值 这里的a和b和传进来的a和b是独立的
    // 也就是说局部变量会被copy一份到结构体内部
    int a; 
    int *b;
    
    __testBlock_block_impl_0(void *fp, struct __testBlock_block_desc_0 *desc, int _a, int *_b, int flags=0) : a(_a), b(_b) {
      impl.isa = &_NSConcreteStackBlock;
      impl.Flags = flags;
      impl.FuncPtr = fp;
      Desc = desc;
    }
  };
  
  static void __testBlock_block_func_0(struct __testBlock_block_impl_0 *__cself) {
    int a = __cself->a; // bound by copy
    int *b = __cself->b; // bound by copy
 
    // 访问结构体自己的局部变量a和b，全局变量c的值可以直接访问
    NSLog((NSString *)&__NSConstantStringImpl__var_folders_6__qrgykwmd2_g_zcqhyrtwzr240000gn_T_main1_dda951_mi_1,a, (*b) , c);
  }

  static struct __testBlock_block_desc_0 {
    size_t reserved;
    size_t Block_size;
  } __testBlock_block_desc_0_DATA = { 0, sizeof(struct __testBlock_block_impl_0)};
  
  void testBlock() {
      int a = 3;
      static int b = 5;
      // 当我们 定义一个block时，会将 局部变量a的值、静态变量的指针 传递给结构体，注意并没有将全局变量c的任何东西传递给结构体
      void(*block)(void) = ((void (*)())&__testBlock_block_impl_0((void *)__testBlock_block_func_0, &__testBlock_block_desc_0_DATA, a, &b));
  }
  ```
  
  * **局部变量**  
    局部变量的值会被完整的copy一份保存在结构体内部。block里面的局部变量和外面的变量是完全独立的存在，所以不能在block里面直接修改局部变量的值
  
  * **全局变量**  
    全局变量不会被结构体持有。block里面可以直接访问和修改全局变量

  * **静态变量**   
    会将静态变量的指针copy一份保存在结构体内部。因此block内部可以直接修改静态变量的值

## __block底层实现

  ```objc
  void testBlock() {
    __block int a = 3;
    void(^block)(void) = ^{
        NSLog(@"%d",a);
    };
  }
  ```
  对应c++实现：
  ```c++
  // 被__block 修饰的变量 底层实际上是这么一个结构体
  struct __Block_byref_a_1 {
    void *__isa;
    __Block_byref_a_1 *__forwarding;
    int __flags;
    int __size;
    int a;
  };

  struct __testBlock_block_impl_0 {
    struct __block_impl impl;
    struct __testBlock_block_desc_0* Desc;
    
    // block里面持有该变量对应的结构体变量的指针
    __Block_byref_a_1 *a; // by ref
    
    __testBlock_block_impl_0(void *fp, struct __testBlock_block_desc_0 *desc, __Block_byref_a_1 *_a, int flags=0) : a(_a->__forwarding) {
      impl.isa = &_NSConcreteStackBlock;
      impl.Flags = flags;
      impl.FuncPtr = fp;
      Desc = desc;
    }
  };
  
  static void __testBlock_block_func_0(struct __testBlock_block_impl_0 *__cself) {
      __Block_byref_a_1 *a = __cself->a; // bound by ref
      
      // block方法内部访问的也是变量对应的结构体指针
      NSLog((NSString *)&__NSConstantStringImpl__var_folders_6__qrgykwmd2_g_zcqhyrtwzr240000gn_T_main1_97e46b_mi_1,(a->__forwarding->a));
   }
   
  // 该方法会在block被copy到堆上面时，对局部变量对应的结构体变量的引用计数加1
  static void __testBlock_block_copy_0(struct __testBlock_block_impl_0*dst, struct __testBlock_block_impl_0*src) {_Block_object_assign((void*)&dst->a, (void*)src->a, 8/*BLOCK_FIELD_IS_BYREF*/);}
  
  // 该方法会在block从堆空间移除时，对局部变量对应的结构体变量的引用计数减1
  static void __testBlock_block_dispose_0(struct __testBlock_block_impl_0*src) {_Block_object_dispose((void*)src->a, 8/*BLOCK_FIELD_IS_BYREF*/);}

  static struct __testBlock_block_desc_0 {
    size_t reserved;
    size_t Block_size;
    void (*copy)(struct __testBlock_block_impl_0*, struct __testBlock_block_impl_0*);
    void (*dispose)(struct __testBlock_block_impl_0*);
  } __testBlock_block_desc_0_DATA = { 0, sizeof(struct __testBlock_block_impl_0), __testBlock_block_copy_0, __testBlock_block_dispose_0};
  
  void testBlock() {
      __attribute__((__blocks__(byref))) __Block_byref_a_1 a = {(void*)0,(__Block_byref_a_1 *)&a, 0, sizeof(__Block_byref_a_1), 3};
      void(*block)(void) = ((void (*)())&__testBlock_block_impl_0((void *)__testBlock_block_func_0, &__testBlock_block_desc_0_DATA, (__Block_byref_a_1 *)&a, 570425344));
  }
  ```
  
  ## block 类型
  
  * **__NSGlobalBlock__**  
    没有访问任何局部变量的block，在内存中存储在**数据段**

  * **__NSStackBlock__**  
    访问了局部变量的block，在内存中存储在**栈空间**
    
  * **__NSMallocBlock__**   
    __NSStackBlock__ 调用copy，在内存中存储在**堆空间**
  

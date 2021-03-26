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
  @interface Person : NSObject
  @property (nonatomic, copy) NSString *name;
  @end

  @implementation Person
  @end

  int c = 4;
  void testBlock() {
      int a = 3;
      static int b = 5;
      Person *p = [[Person alloc] init];
      p.name = @"zhangSan";
      __weak typeof(p) p1 = p;

      void(^block)(void) = ^{
          NSLog(@"%d %d %d %@ %@",a, b , c, p, p1);
      };
  }
  ```
  
  对应c++实现：
  
  ```c++
  int c = 4;

  struct __testBlock_block_impl_0 {
    struct __block_impl impl;
    struct __testBlock_block_desc_0* Desc;
    
    // 结构体内部会新增变量保存传递过来的局部变量的值 这里定义的变量和传递进来的变量是完成独立的
    int a; 
    int *b;
    Person *__strong p; // 外面定义的局部变量是用什么修饰 这里就是用什么修饰
    Person *__weak p1;
    
    __testBlock_block_impl_0(void *fp, struct __testBlock_block_desc_0 *desc, int _a, int *_b, Person *__strong _p, Person *__weak _p1, int flags=0) : a(_a), b(_b), p(_p), p1(_p1) {
      impl.isa = &_NSConcreteStackBlock;
      impl.Flags = flags;
      impl.FuncPtr = fp;
      Desc = desc;
    }
  };
  
  static void __testBlock_block_func_0(struct __testBlock_block_impl_0 *__cself) {
    int a = __cself->a; // bound by copy
    int *b = __cself->b; // bound by copy
    Person *__strong p = __cself->p; // bound by copy
    Person *__weak p1 = __cself->p1; // bound by copy
 
    // 访问结构体自己的内部定义的变量，全局变量c的值可以直接访问
    NSLog((NSString *)&__NSConstantStringImpl__var_folders_6__qrgykwmd2_g_zcqhyrtwzr240000gn_T_main1_3e09c7_mi_1,a, (*b) , c, p, p1);
  }

  // 当block被copy到堆上时，会根据 结构体内部 对象类型 的修饰符 对block内部引用的 对象的引用计数加1
  static void __testBlock_block_copy_0(struct __testBlock_block_impl_0*dst, struct __testBlock_block_impl_0*src) {_Block_object_assign((void*)&dst->p, (void*)src->p, 3/*BLOCK_FIELD_IS_OBJECT*/);_Block_object_assign((void*)&dst->p1, (void*)src->p1, 3/*BLOCK_FIELD_IS_OBJECT*/);}
  
  // 当block从堆上移除，会根据 结构体内部 对象类型 的修饰符 对block内部引用的 对象的引用计数减1
  static void __testBlock_block_dispose_0(struct __testBlock_block_impl_0*src) {_Block_object_dispose((void*)src->p, 3/*BLOCK_FIELD_IS_OBJECT*/);_Block_object_dispose((void*)src->p1, 3/*BLOCK_FIELD_IS_OBJECT*/);}

  static struct __testBlock_block_desc_0 {
    size_t reserved;
    size_t Block_size;
    void (*copy)(struct __testBlock_block_impl_0*, struct __testBlock_block_impl_0*);
    void (*dispose)(struct __testBlock_block_impl_0*);
  } __testBlock_block_desc_0_DATA = { 0, sizeof(struct __testBlock_block_impl_0), __testBlock_block_copy_0, __testBlock_block_dispose_0};
  
  void testBlock() {
      int a = 3;
      static int b = 5;
      
      Person *p = ((Person *(*)(id, SEL))(void *)objc_msgSend)((id)((Person *(*)(id, SEL))(void *)objc_msgSend)((id)objc_getClass("Person"), sel_registerName("alloc")), sel_registerName("init"));
      ((void (*)(id, SEL, NSString *))(void *)objc_msgSend)((id)p, sel_registerName("setName:"), (NSString *)&__NSConstantStringImpl__var_folders_6__qrgykwmd2_g_zcqhyrtwzr240000gn_T_main1_3e09c7_mi_0);
      
      __attribute__((objc_ownership(weak))) typeof(p) p1 = p;
      
      // 当我们 定义一个block时，会将 局部变量的值、静态变量的指针 传递给结构体，注意并没有将全局变量c的任何东西传递给结构体
      void(*block)(void) = ((void (*)())&__testBlock_block_impl_0((void *)__testBlock_block_func_0, &__testBlock_block_desc_0_DATA, a, &b, p, p1, 570425344));
  }
  ```
  
  * **局部变量**  
    局部变量的值会被完整的copy一份保存在结构体内部。block里面的局部变量和外面的变量是完全独立的存在，所以不能在block里面直接修改局部变量的值。如果局部变量是一个对象类型，则block内部会根据定义局部变量时使用的修饰符（strong， weak）在结构体内部相应的**强/弱**引用该局部变量，也因此会造成循环引用
  
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
    __Block_byref_a_1 *__forwarding; // 指向自己的一个指针
    int __flags;
    int __size;
    int a; // 当初局部变量的值
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
      // 这里传递的是a结构体的地址，所以block内部可以修改a的值，注意修改的也是a这个结构体里面保存的a的值
      void(*block)(void) = ((void (*)())&__testBlock_block_impl_0((void *)__testBlock_block_func_0, &__testBlock_block_desc_0_DATA, (__Block_byref_a_1 *)&a, 570425344));
  }
  
  ```
  
  当使用__block修饰一个局部变量时，该变量会被包装成一个__Block_byref_a_1类型的结构体，然后将该结构体指针传递到block内部，所以可以在block内部修改局部变量的值，注意此时修改的是局部变量对应的结构体里面保存的值
  
  ## block 类型
  
  * **__NSGlobalBlock__**  局部static变量算不算？？
    没有访问任何局部变量的block，在内存中存储在**数据段**

  * **__NSStackBlock__**  
    访问了局部变量的block，在内存中存储在**栈空间**。ARC环境下编译器会对该类型的block做优化，将block自动copy到堆上：
    1. block作为函数返回值时
    2. 将block赋值给__strong指针时
    3. block作为Cocoa API中方法名含有usingBlock的方法参数时
    4. block作为GCD API的方法参数时
    
  * **__NSMallocBlock__**   
    __NSStackBlock__ 调用copy，在内存中存储在**堆空间**
  

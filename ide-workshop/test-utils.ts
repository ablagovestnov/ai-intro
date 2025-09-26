/**
 * Утилиты для тестирования работы AI-плагинов в IDE
 * 
 * Содержит разнообразные функции для проверки:
 * - Генерации кода
 * - Объяснения логики
 * - Рефакторинга
 * - Поиска багов
 * - Написания тестов
 */

// 1. Асинхронная функция с обработкой ошибок
/**
 * Асинхронная функция для получения данных пользователя по его ID
 * @param userId - уникальный идентификатор пользователя (обязательный параметр)
 * @returns Объект с полями id, name, email при успехе, или null при ошибке
 */
export async function fetchUserData(userId: string): Promise<{ id: string; name: string; email: string } | null> {
  if (!userId) {
    throw new Error('User ID is required');
  }

  try {
    const response = await fetch(`/api/users/${userId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      id: data.id,
      name: data.name,
      email: data.email
    };
  } catch (error) {
    console.error('Failed to fetch user data:', error);
    return null;
  }
}

// 2. Функция с сложной логикой и несколькими путями выполнения
export function calculateDiscount(price: number, userLevel: 'basic' | 'premium' | 'vip', isHoliday: boolean): number {
  console.log('calculateDiscount called with:', { price, userLevel, isHoliday });
  
  if (price < 0) {
    throw new Error('Price cannot be negative');
  }

  let discount = 0;

  // Базовые скидки по уровню
  switch (userLevel) {
    case 'premium':
      discount = 0.1;
      console.log('Premium discount applied: 10%');
      break;
    case 'vip':
      discount = 0.2;
      console.log('VIP discount applied: 20%');
      break;
    case 'basic':
      discount = 0.05;
      console.log('Basic discount applied: 5%');
      break;
    default:
      console.warn('Unknown user level:', userLevel);
      discount = 0.05;
  }

  console.log('Base discount:', discount);

  // Дополнительная скидка на праздник
  if (isHoliday) {
    discount += 0.1;
    console.log('Holiday bonus discount applied: +10%');
  }

  // Максимальная скидка 30%
  const finalDiscount = Math.min(discount, 0.3);
  console.log('Final discount before cap:', discount, 'After cap:', finalDiscount);

  const result = price * (1 - finalDiscount);
  console.log('Final price:', result);
  
  return result;
}

// 3. Работа с массивами и преобразование данных
export interface Order {
  id: string;
  amount: number;
  status: 'pending' | 'shipped' | 'delivered' | 'cancelled';
  items: Array<{
    productId: string;
    quantity: number;
    price: number;
  }>;
}

export function getCustomerStats(orders: Order[]): {
  totalSpent: number;
  orderCount: number;
  averageOrderValue: number;
  deliveredCount: number;
} {
  const completedOrders = orders.filter(order => order.status === 'delivered');
  
  const totalSpent = completedOrders.reduce((sum, order) => {
    return sum + order.amount;
  }, 0);

  return {
    totalSpent,
    orderCount: completedOrders.length,
    averageOrderValue: completedOrders.length > 0 ? totalSpent / completedOrders.length : 0,
    deliveredCount: completedOrders.length
  };
}

// 4. Работа с промисами и асинхронными операциями
export async function processBatchOperations<T>(items: T[], processor: (item: T) => Promise<void>): Promise<{ successCount: number; errorCount: number }> {
  const results = await Promise.allSettled(items.map(item => processor(item)));
  
  const successCount = results.filter(result => result.status === 'fulfilled').length;
  const errorCount = results.filter(result => result.status === 'rejected').length;

  return { successCount, errorCount };
}

// 5. Простая утилита валидации
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// 6. Работа с датами
export function getDaysUntil(targetDate: Date): number {
  const now = new Date();
  const diffTime = targetDate.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}
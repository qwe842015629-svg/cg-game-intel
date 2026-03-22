import client from './client'

export interface RechargeVariation {
  variation_id: string
  name: string
  price: string
  is_available: boolean
}

export interface RechargeField {
  key: string
  name: string
  label: string
  type: string
  required: boolean
  placeholder: string
  description: string
  options: string[]
}

export interface RechargeCatalogProduct {
  binding_id: number
  provider_uuid: string
  product_id: string
  product_name: string
  image_url: string
  status: string
  order_supported: boolean
  is_balance: boolean
  fields: RechargeField[]
  variations: RechargeVariation[]
}

export interface RechargeCatalogResponse {
  game: {
    id: number
    slug: string
    title: string
  }
  count: number
  results: RechargeCatalogProduct[]
}

export interface RechargeOrderItem {
  id: number
  out_trade_no: string
  idempotency_key?: string
  status: string
  external_status: string
  external_order_id: string
  product_name: string
  variation_name: string
  quantity: number
  total_amount: string
  error_code: string
  error_message: string
  created_at: string
  updated_at: string
  completed_at: string | null
}

export interface RechargeOrdersResponse {
  items: RechargeOrderItem[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface RechargeOrderCreatePayload {
  binding_id: number
  variation_id: string
  quantity?: number
  idempotency_key?: string
  dynamic_fields?: Record<string, string>
  recharge_amount?: number
}

export interface ChargeXInventoryProviderSummary {
  id: string
  layout: string
  product_count: number
  in_stock: number
  out_of_stock: number
  unknown: number
  failed_detail: number
}

export interface ChargeXInventoryProductItem {
  provider_uuid: string
  provider_layout: string
  product_id: string
  product_name: string
  product_name_cn: string
  product_name_tw: string
  product_name_en: string
  localized_name: string
  image_url: string
  list_status: string
  order_supported: boolean
  is_balance: boolean
  discount: string
  fields_count: number
  total_variations: number
  available_variations: number
  unavailable_variations: number
  inventory_status: 'in_stock' | 'out_of_stock' | 'unknown'
  detail_error_code: string
  detail_error_message: string
}

export interface ChargeXInventoryVariation {
  variation_id: string
  name: string
  name_cn: string
  name_tw: string
  name_en: string
  localized_name: string
  price: string
  is_available: boolean
}

export interface ChargeXInventoryProductDetailResponse {
  provider_uuid: string
  product_id: string
  product_name: string
  product_name_cn: string
  product_name_tw: string
  product_name_en: string
  localized_name: string
  image_url: string
  status: string
  order_supported: boolean
  is_balance: boolean
  fields: RechargeField[]
  variations: ChargeXInventoryVariation[]
}

export interface RechargeInventoryOrderCreatePayload {
  provider_uuid: string
  product_id: string
  variation_id: string
  quantity?: number
  idempotency_key?: string
  dynamic_fields?: Record<string, string>
  recharge_amount?: number
}

export interface RechargeInventoryWechatPayCreatePayload
  extends RechargeInventoryOrderCreatePayload {}

export interface RechargeInventoryWechatPayCreateResponse {
  out_trade_no: string
  code_url: string
  prepay_id: string
  pay_status: string
  trade_state: string
  total_fee: string
  total_amount: string
  order: RechargeOrderItem
}

export interface RechargeInventoryWechatPayStatusResponse {
  out_trade_no: string
  pay_status: 'success' | 'notpay' | 'userpaying' | 'closed' | 'payerror' | 'revoked' | 'refund' | 'unknown'
  trade_state: string
  trade_state_desc: string
  transaction_id: string
  time_end: string
  order: RechargeOrderItem
}

export interface ChargeXInventorySnapshotResponse {
  generated_at: string
  provider_count: number
  product_count: number
  is_complete: boolean
  sync_status: 'running' | 'completed' | 'failed' | 'skipped_locked' | 'unknown'
  run_started_at: string
  run_finished_at: string
  run_duration_seconds: number
  last_error: {
    code: string
    message: string
  }
  scanned_products: number
  expected_products: number
  stats: {
    in_stock: number
    out_of_stock: number
    unknown: number
    failed_detail: number
    rate_limit_hit?: number
  }
  health: {
    snapshot_age_seconds: number | null
    delay_status: 'fresh' | 'delayed' | 'stale' | 'unknown'
    delay_warn_seconds: number
    delay_stale_seconds: number
    auto_refresh_recommended_seconds: number
  }
  providers: ChargeXInventoryProviderSummary[]
  cache_ttl_seconds: number
  items: ChargeXInventoryProductItem[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export const getRechargeCatalog = async (gameSlug: string): Promise<RechargeCatalogResponse> => {
  const slug = String(gameSlug || '').trim()
  if (!slug) throw new Error('game slug is required')
  const response: any = await client.get(`/recharge/catalog/${encodeURIComponent(slug)}/`)
  return {
    game: response?.game || { id: 0, slug, title: '' },
    count: Number(response?.count || 0),
    results: Array.isArray(response?.results) ? response.results : [],
  }
}

export const createRechargeOrder = async (
  payload: RechargeOrderCreatePayload
): Promise<RechargeOrderItem> => {
  const response: any = await client.post('/recharge/orders/', payload)
  return response as RechargeOrderItem
}

export const getRechargeOrders = async (params?: {
  page?: number
  limit?: number
  status?: string
}): Promise<RechargeOrdersResponse> => {
  const response: any = await client.get('/recharge/orders/', { params: params || {} })
  return {
    items: Array.isArray(response?.items) ? response.items : [],
    total: Number(response?.total || 0),
    page: Number(response?.page || 1),
    limit: Number(response?.limit || 20),
    total_pages: Number(response?.total_pages || 0),
  }
}

export const getRechargeOrder = async (outTradeNo: string): Promise<RechargeOrderItem> => {
  const value = String(outTradeNo || '').trim()
  if (!value) throw new Error('out_trade_no is required')
  const response: any = await client.get(`/recharge/orders/${encodeURIComponent(value)}/`)
  return response as RechargeOrderItem
}

export const getChargeXInventorySnapshot = async (params?: {
  provider?: string
  inventory_status?: 'in_stock' | 'out_of_stock' | 'unknown' | ''
  search?: string
  page?: number
  limit?: number
}): Promise<ChargeXInventorySnapshotResponse> => {
  const response: any = await client.get('/recharge/inventory-snapshot/', { params: params || {} })
  return {
    generated_at: String(response?.generated_at || ''),
    provider_count: Number(response?.provider_count || 0),
    product_count: Number(response?.product_count || 0),
    is_complete: Boolean(response?.is_complete),
    sync_status: String(response?.sync_status || 'unknown') as
      | 'running'
      | 'completed'
      | 'failed'
      | 'skipped_locked'
      | 'unknown',
    run_started_at: String(response?.run_started_at || ''),
    run_finished_at: String(response?.run_finished_at || ''),
    run_duration_seconds: Number(response?.run_duration_seconds || 0),
    last_error: {
      code: String(response?.last_error?.code || ''),
      message: String(response?.last_error?.message || ''),
    },
    scanned_products: Number(response?.scanned_products || 0),
    expected_products: Number(response?.expected_products || 0),
    stats: {
      in_stock: Number(response?.stats?.in_stock || 0),
      out_of_stock: Number(response?.stats?.out_of_stock || 0),
      unknown: Number(response?.stats?.unknown || 0),
      failed_detail: Number(response?.stats?.failed_detail || 0),
      rate_limit_hit: Number(response?.stats?.rate_limit_hit || 0),
    },
    health: {
      snapshot_age_seconds:
        response?.health?.snapshot_age_seconds === null
          ? null
          : Number(response?.health?.snapshot_age_seconds || 0),
      delay_status: String(response?.health?.delay_status || 'unknown') as
        | 'fresh'
        | 'delayed'
        | 'stale'
        | 'unknown',
      delay_warn_seconds: Number(response?.health?.delay_warn_seconds || 600),
      delay_stale_seconds: Number(response?.health?.delay_stale_seconds || 1200),
      auto_refresh_recommended_seconds: Number(
        response?.health?.auto_refresh_recommended_seconds || 60
      ),
    },
    providers: Array.isArray(response?.providers) ? response.providers : [],
    cache_ttl_seconds: Number(response?.cache_ttl_seconds || 0),
    items: Array.isArray(response?.items) ? response.items : [],
    total: Number(response?.total || 0),
    page: Number(response?.page || 1),
    limit: Number(response?.limit || 50),
    total_pages: Number(response?.total_pages || 0),
  }
}

export const getChargeXInventoryProductDetail = async (params: {
  provider_uuid: string
  product_id: string
}): Promise<ChargeXInventoryProductDetailResponse> => {
  const providerUuid = String(params?.provider_uuid || '').trim()
  const productId = String(params?.product_id || '').trim()
  if (!providerUuid || !productId) {
    throw new Error('provider_uuid and product_id are required')
  }

  const response: any = await client.get('/recharge/inventory-product/', {
    params: {
      provider_uuid: providerUuid,
      product_id: productId,
    },
  })

  return {
    provider_uuid: String(response?.provider_uuid || providerUuid),
    product_id: String(response?.product_id || productId),
    product_name: String(response?.product_name || ''),
    product_name_cn: String(response?.product_name_cn || ''),
    product_name_tw: String(response?.product_name_tw || ''),
    product_name_en: String(response?.product_name_en || ''),
    localized_name: String(response?.localized_name || response?.product_name || ''),
    image_url: String(response?.image_url || ''),
    status: String(response?.status || ''),
    order_supported: Boolean(response?.order_supported),
    is_balance: Boolean(response?.is_balance),
    fields: Array.isArray(response?.fields) ? response.fields : [],
    variations: Array.isArray(response?.variations) ? response.variations : [],
  }
}

export const createRechargeInventoryOrder = async (
  payload: RechargeInventoryOrderCreatePayload
): Promise<RechargeOrderItem> => {
  const response: any = await client.post('/recharge/inventory-orders/', payload)
  return response as RechargeOrderItem
}

export const createRechargeInventoryWechatPay = async (
  payload: RechargeInventoryWechatPayCreatePayload
): Promise<RechargeInventoryWechatPayCreateResponse> => {
  const response: any = await client.post('/recharge/wechat-pay/inventory/create/', payload)
  return response as RechargeInventoryWechatPayCreateResponse
}

export const getRechargeInventoryWechatPayStatus = async (
  outTradeNo: string
): Promise<RechargeInventoryWechatPayStatusResponse> => {
  const value = String(outTradeNo || '').trim()
  if (!value) throw new Error('out_trade_no is required')
  const response: any = await client.get('/recharge/wechat-pay/inventory/status/', {
    params: { out_trade_no: value },
  })
  return response as RechargeInventoryWechatPayStatusResponse
}

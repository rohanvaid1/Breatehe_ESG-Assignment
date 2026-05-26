export type ListResponse<T> = { results?: T[]; data?: T[] } | T[]

export const unwrapList = <T>(payload: ListResponse<T>): T[] => {
  if (Array.isArray(payload)) {
    return payload
  }
  return payload.results ?? payload.data ?? []
}

export const getApiBaseUrl = () => {
  if (process.env.NEXT_PUBLIC_OUTPUT_MODE === "export") {
    return "."; // 相対パスを返す
  }
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_BASEPATH;
  }
  // undefinedでなければAPI_BASEPATHを返す
  if (process.env.API_BASEPATH) {
    return process.env.API_BASEPATH;
  }
  return process.env.NEXT_PUBLIC_API_BASEPATH;
};

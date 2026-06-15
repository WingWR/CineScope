import { useCallback, useEffect, useState } from "react";
import type {
  FeatureSchemaResponse,
  RevenuePredictionRequest,
  RevenuePredictionResponse,
} from "../../../entities/movie/types";
import { getUserFacingApiMessage } from "../../../shared/api/errors";
import { revenuePredictionApi } from "../api";

type RevenuePredictionState = {
  schema: FeatureSchemaResponse | null;
  result: RevenuePredictionResponse | null;
  isLoading: boolean;
  isSchemaLoading: boolean;
  errorMessage: string | null;
};

export function useRevenuePrediction() {
  const [schema, setSchema] = useState<FeatureSchemaResponse | null>(null);
  const [isSchemaLoading, setIsSchemaLoading] = useState(true);
  const [result, setResult] = useState<RevenuePredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Fetch schema on mount
  useEffect(() => {
    let isActive = true;
    setIsSchemaLoading(true);

    void revenuePredictionApi
      .getSchema()
      .then((s) => {
        if (isActive) setSchema(s);
      })
      .catch(() => {
        // Schema fetch failure is non-fatal; we have hardcoded defaults
        if (isActive) setSchema(null);
      })
      .finally(() => {
        if (isActive) setIsSchemaLoading(false);
      });

    return () => {
      isActive = false;
    };
  }, []);

  const predict = useCallback((request: RevenuePredictionRequest) => {
    let isActive = true;
    setIsLoading(true);
    setErrorMessage(null);
    setResult(null);

    void revenuePredictionApi
      .predict(request)
      .then((response) => {
        if (isActive) setResult(response);
      })
      .catch((error: unknown) => {
        if (isActive) {
          setResult(null);
          setErrorMessage(getUserFacingApiMessage(error));
        }
      })
      .finally(() => {
        if (isActive) setIsLoading(false);
      });

    return () => {
      isActive = false;
    };
  }, []);

  return { schema, result, isLoading, isSchemaLoading, errorMessage, predict } satisfies RevenuePredictionState & {
    predict: (request: RevenuePredictionRequest) => () => void;
  };
}

"use client";

import { ApiConnectionError } from "@/components/ApiConnectionError";
import { Button } from "@chakra-ui/react";
import { useEffect } from "react";

type Props = {
  error: Error & { digest?: string };
  reset: () => void;
};

export default function ErrorPage({ error, reset }: Props) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <>
      <ApiConnectionError isServerSide={false} />
      <Button onClick={reset}>リトライする</Button>
    </>
  );
}

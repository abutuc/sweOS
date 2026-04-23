"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { api, type Profile } from "@/lib/api";
import { isProfileOnboardingComplete } from "@/lib/onboarding";

export function useOnboardingStatus(options?: { redirectIfIncomplete?: boolean }) {
  const pathname = usePathname();
  const router = useRouter();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    void api
      .getProfile()
      .then((response) => {
        if (!active) {
          return;
        }

        setProfile(response.data);

        if (
          options?.redirectIfIncomplete &&
          pathname !== "/onboarding" &&
          !isProfileOnboardingComplete(response.data)
        ) {
          router.replace("/onboarding");
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [options?.redirectIfIncomplete, pathname, router]);

  return {
    profile,
    isLoading,
    isComplete: profile ? isProfileOnboardingComplete(profile) : false,
  };
}

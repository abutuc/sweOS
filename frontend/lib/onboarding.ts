import type { Profile } from "@/lib/api";

export function isProfileOnboardingComplete(profile: Profile) {
  const hasIdentityShape =
    Boolean(profile.headline) || Boolean(profile.currentRole) || Boolean(profile.summary);
  const hasDirection = Boolean(profile.targetRole) || profile.targetRoles.length > 0;
  const hasSkillSignal = profile.stack.length > 0;

  return hasIdentityShape && hasDirection && hasSkillSignal;
}

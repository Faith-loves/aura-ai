import Skeleton from "./Skeleton";


export default function PageLoading() {
  return (
    <div
      className="
        mx-auto
        w-full
        max-w-[1500px]
      "
      aria-busy="true"
      aria-label="Loading content"
    >
      <div
        className="
          flex
          flex-col
          gap-3
        "
      >
        <Skeleton
          className="
            h-4
            w-24
          "
        />

        <Skeleton
          className="
            h-9
            w-full
            max-w-md
          "
        />

        <Skeleton
          className="
            h-4
            w-full
            max-w-xl
          "
        />
      </div>

      <div
        className="
          mt-8
          grid
          grid-cols-1
          gap-4
          sm:grid-cols-2
          xl:grid-cols-4
        "
      >
        {Array.from(
          {
            length: 4,
          }
        ).map(
          (
            _,
            index
          ) => (
            <div
              key={index}
              className="
                rounded-2xl
                border
                border-[#1D2942]
                bg-[#0D1321]
                p-5
              "
            >
              <div
                className="
                  flex
                  items-start
                  justify-between
                "
              >
                <Skeleton
                  className="
                    h-10
                    w-10
                    rounded-xl
                  "
                />

                <Skeleton
                  className="
                    h-4
                    w-4
                  "
                />
              </div>

              <Skeleton
                className="
                  mt-5
                  h-8
                  w-16
                "
              />

              <Skeleton
                className="
                  mt-3
                  h-4
                  w-28
                "
              />

              <Skeleton
                className="
                  mt-2
                  h-3
                  w-20
                "
              />
            </div>
          )
        )}
      </div>

      <div
        className="
          mt-5
          grid
          gap-5
          xl:grid-cols-[1.5fr_0.8fr]
        "
      >
        <div
          className="
            rounded-2xl
            border
            border-[#1D2942]
            bg-[#0D1321]
            p-5
          "
        >
          <Skeleton
            className="
              h-5
              w-36
            "
          />

          <Skeleton
            className="
              mt-2
              h-3
              w-48
            "
          />

          <div
            className="
              mt-6
              rounded-2xl
              border
              border-[#162036]
              p-5
            "
          >
            <Skeleton
              className="
                h-4
                w-3/4
              "
            />

            <Skeleton
              className="
                mt-5
                h-2
                w-full
                rounded-full
              "
            />

            <div
              className="
                mt-6
                grid
                gap-3
                md:grid-cols-3
              "
            >
              {Array.from(
                {
                  length: 3,
                }
              ).map(
                (
                  _,
                  index
                ) => (
                  <Skeleton
                    key={index}
                    className="
                      h-20
                      w-full
                      rounded-xl
                    "
                  />
                )
              )}
            </div>
          </div>
        </div>

        <div
          className="
            rounded-2xl
            border
            border-[#1D2942]
            bg-[#0D1321]
            p-5
          "
        >
          <Skeleton
            className="
              h-5
              w-28
            "
          />

          <Skeleton
            className="
              mt-2
              h-3
              w-40
            "
          />

          <div
            className="
              mt-6
              space-y-3
            "
          >
            {Array.from(
              {
                length: 5,
              }
            ).map(
              (
                _,
                index
              ) => (
                <Skeleton
                  key={index}
                  className="
                    h-11
                    w-full
                    rounded-xl
                  "
                />
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
}